from django.db import models
from django.utils.timezone import now
from sklearn.preprocessing import MinMaxScaler

from places.models import District, City
from predictors.abstracts.DataPreprocessor import DataPreprocessor
from predictors.abstracts.Predictor import Predictor
from users.models import AllergicUser, Travel
import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.saving import register_keras_serializable
import tensorflow as tf
import tensorflow.keras.backend as K
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime
from sklearn.decomposition import PCA


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to="predictors/models/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
            self.last_update_date = now()

        if self.file_path:
            file_extension = os.path.splitext(self.file_path.name)[1]
            new_file_name = f"{self.name}-{self.version}{file_extension}"
            self.file_path.name = new_file_name

        super().save(*args, **kwargs)

    def __str__(self):
        return (self.name + ": last updated at " + str(self.last_update_date.day) +
                "/" + str(self.last_update_date.month) + "/" + str(self.last_update_date.year))

    class Meta:
        db_table = "models"
        db_table_comment = "Table that contains AI model information for AllerGeo"


class AIAllergyAttackPrediction(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    date = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")
    ai_prediction = models.FloatField(blank=True, null=True, default=0)
    had_allergy_attack = models.BooleanField(blank=True, null=True)
    model = models.ForeignKey(AIModel, on_delete=models.PROTECT, db_column="model_id", blank=True, null=True)
    travel = models.ForeignKey(Travel, on_delete=models.PROTECT, default=None, null=True, blank=True)
    selected_latitude = models.FloatField(null=True, blank=True)
    selected_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.user) + ' / ' + str(self.ai_prediction) + " - " + str(self.had_allergy_attack) + ("" if self.model is None else " model: " + self.model.name)

    class Meta:
        db_table = "ai_allergy_attack_predictions"
        db_table_comment = "Table that contains predictions and actual results for each district at the travel for AllerGeo"


class GeneralLSTMModel(Predictor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sequence_length = self.params.get('sequence_length', 7)
        self.activation_function = self.params.get('activation', 'tanh')
        self.hidden_units = self.params.get('hidden_units', 64)
        self.batch_size = self.params.get('batch_size', 28)
        self.epochs = self.params.get('epochs', 20)
        self.learning_rate = self.params.get('learning_rate', 0.003)
        self.dropout_rate = self.params.get('dropout', 0.2)
        self.loss = self.params.get('loss', 'mse')
        self.optimizer = self.params.get('optimizer', 'adam')
        self.input_shape = None
        self.output_dim = None

    @register_keras_serializable()
    def r2_score_keras(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        ss_res = K.sum(K.square(y_true - y_pred))
        ss_tot = K.sum(K.square(y_true - K.mean(y_true)))
        return 1 - (ss_res / (ss_tot + K.epsilon()))

    def __create_sequences(self, x_df: pd.DataFrame, y_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        x, y = [], []

        full_df = pd.concat([x_df.reset_index(drop=True), y_df.reset_index(drop=True)], axis=1)

        full_df['LocationId'] = full_df.apply(
            lambda row: int(row['DistrictId']) if pd.notnull(row['DistrictId']) else f"city_{int(row['CityId'])}",
            axis=1
        )
        full_df = full_df.sort_values(by=['Year', 'Month', 'Day'])

        feature_cols = x_df.columns.difference(['DistrictId', 'CityId', 'Year', 'Month', 'Day'])
        target_cols = y_df.columns

        for loc_id, group in full_df.groupby('LocationId'):
            x_values = group[feature_cols].values
            y_values = group[target_cols].values

            for i in range(len(group) - self.sequence_length):
                x_seq = x_values[i:i + self.sequence_length]
                y_seq = y_values[i + self.sequence_length]
                x.append(x_seq)
                y.append(y_seq)

        return np.array(x), np.array(y)

    def build_model(self):
        self.model = Sequential([
            Input(shape=self.input_shape),
            LSTM(self.hidden_units, activation=self.activation_function),
            Dropout(self.dropout_rate),
            Dense(self.output_dim, activation='linear')
        ])
        self.__compile()

    def __compile(self):
        if self.optimizer == 'adam':
            optimizer = Adam(learning_rate=self.learning_rate)
        elif self.optimizer == 'sgd':
            optimizer = tf.keras.optimizers.SGD(learning_rate=self.learning_rate)
        elif self.optimizer == 'rmsprop':
            optimizer = tf.keras.optimizers.RMSprop(learning_rate=self.learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {self.optimizer}")

        self.model.compile(
            optimizer=optimizer,
            loss=self.loss,
            metrics=['mae', 'mse', self.r2_score_keras]
        )

    def train(self, x_train: pd.DataFrame, y_train: pd.DataFrame):
        x_seq, y_seq = self.__create_sequences(x_train, y_train)
        self.input_shape = (x_seq.shape[1], x_seq.shape[2])
        self.output_dim = y_seq.shape[1]
        self.build_model()
        self.model.fit(x_seq, y_seq, epochs=self.epochs, batch_size=self.batch_size, verbose=1)

    def evaluate(self, x_test: pd.DataFrame, y_test: pd.DataFrame, save_model: bool = True) -> dict:
        x_seq, y_seq = self.__create_sequences(x_test, y_test)
        y_pred = self.model.predict(x_seq)
        return y_pred

    def predict(self, x: pd.DataFrame):
        x_last = x.values[-self.sequence_length:]
        x_seq = np.expand_dims(x_last, axis=0)
        prediction = self.model.predict(x_seq)[0]
        rounded_prediction = np.round(prediction).astype(int)
        return rounded_prediction

    def save_model(self, filename: str):
        dir_path = os.path.join(os.getcwd(), 'models')
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, filename)
        self.model.save(path)
        print(f"Model saved to: {path}")

    def load_model(self, filename: str):
        self.model = load_model(filename, custom_objects={'r2_score_keras': self.r2_score_keras})
        self.__compile()

    def fine_tune(self, x: pd.DataFrame, y: pd.DataFrame, epochs: int = 5, save_fine_tuned=False):
        saved_models_cols = ["HoursOfSun", "Health_Arthritis", "Health_SinusPressure", "Health_CommonCold",
                             "Health_Flu", "Health_Migraine", "Health_Asthma", "Pests_Mosquitos", "Pests_IndoorPests",
                             "Pests_OutdoorPests", "Temperature_Minimum_Value", "Temperature_Maximum_Value",
                             "RealFeelTemperature_Minimum_Value", "RealFeelTemperature_Maximum_Value",
                             "RealFeelTemperatureShade_Minimum_Value", "RealFeelTemperatureShade_Maximum_Value",
                             "Day_HasPrecipitation", "Day_PrecipitationProbability", "Day_ThunderstormProbability",
                             "Day_RainProbability", "Day_SnowProbability", "Day_IceProbability", "Day_Wind_Speed_Value",
                             "Day_Wind_Direction_Degrees", "Day_WindGust_Speed_Value", "Day_WindGust_Direction_Degrees",
                             "Day_TotalLiquid_Value", "Day_Rain_Value", "Day_Snow_Value", "Day_Ice_Value",
                             "Day_HoursOfPrecipitation", "Day_HoursOfRain", "Day_HoursOfSnow", "Day_HoursOfIce",
                             "Day_CloudCover", "Day_Evapotranspiration_Value", "Day_SolarIrradiance_Value",
                             "Day_RelativeHumidity_Minimum", "Day_RelativeHumidity_Maximum",
                             "Day_RelativeHumidity_Average", "Day_WetBulbTemperature_Minimum_Value",
                             "Day_WetBulbTemperature_Maximum_Value", "Day_WetBulbTemperature_Average_Value",
                             "Day_WetBulbGlobeTemperature_Minimum_Value", "Day_WetBulbGlobeTemperature_Maximum_Value",
                             "Day_WetBulbGlobeTemperature_Average_Value", "Night_HasPrecipitation",
                             "Night_PrecipitationProbability", "Night_ThunderstormProbability", "Night_RainProbability",
                             "Night_SnowProbability", "Night_IceProbability", "Night_Wind_Speed_Value",
                             "Night_Wind_Direction_Degrees", "Night_WindGust_Speed_Value",
                             "Night_WindGust_Direction_Degrees", "Night_TotalLiquid_Value", "Night_Rain_Value",
                             "Night_Snow_Value", "Night_Ice_Value", "Night_HoursOfPrecipitation", "Night_HoursOfRain",
                             "Night_HoursOfSnow", "Night_HoursOfIce", "Night_CloudCover",
                             "Night_Evapotranspiration_Value", "Night_SolarIrradiance_Value",
                             "Night_RelativeHumidity_Minimum", "Night_RelativeHumidity_Maximum",
                             "Night_RelativeHumidity_Average", "Night_WetBulbTemperature_Minimum_Value",
                             "Night_WetBulbTemperature_Maximum_Value", "Night_WetBulbTemperature_Average_Value",
                             "Night_WetBulbGlobeTemperature_Minimum_Value",
                             "Night_WetBulbGlobeTemperature_Maximum_Value",
                             "Night_WetBulbGlobeTemperature_Average_Value", "AirAndPollen_AirQuality",
                             "AirAndPollen_UVIndex", "Day_PrecipitationIntensity", "Night_PrecipitationIntensity",
                             "Year", "Month", "Day", "Hour", "DayOfYearRatio", "Sun_Rise_Hour", "Sun_Rise_Minute",
                             "Sun_Set_Hour", "Sun_Set_Minute", "CityRegion", "Season_Autumn", "Season_Spring",
                             "Season_Winter", "Day_Wind_Direction_Localized_E", "Day_Wind_Direction_Localized_ENE",
                             "Day_Wind_Direction_Localized_ESE", "Day_Wind_Direction_Localized_N",
                             "Day_Wind_Direction_Localized_NE", "Day_Wind_Direction_Localized_NNE",
                             "Day_Wind_Direction_Localized_NNW", "Day_Wind_Direction_Localized_NW",
                             "Day_Wind_Direction_Localized_S", "Day_Wind_Direction_Localized_SE",
                             "Day_Wind_Direction_Localized_SSE", "Day_Wind_Direction_Localized_SSW",
                             "Day_Wind_Direction_Localized_SW", "Day_Wind_Direction_Localized_W",
                             "Day_Wind_Direction_Localized_WNW", "Day_Wind_Direction_Localized_WSW",
                             "Day_WindGust_Direction_Localized_E", "Day_WindGust_Direction_Localized_ENE",
                             "Day_WindGust_Direction_Localized_ESE", "Day_WindGust_Direction_Localized_N",
                             "Day_WindGust_Direction_Localized_NE", "Day_WindGust_Direction_Localized_NNE",
                             "Day_WindGust_Direction_Localized_NNW", "Day_WindGust_Direction_Localized_NW",
                             "Day_WindGust_Direction_Localized_S", "Day_WindGust_Direction_Localized_SE",
                             "Day_WindGust_Direction_Localized_SSE", "Day_WindGust_Direction_Localized_SSW",
                             "Day_WindGust_Direction_Localized_SW", "Day_WindGust_Direction_Localized_W",
                             "Day_WindGust_Direction_Localized_WNW", "Day_WindGust_Direction_Localized_WSW",
                             "Day_PrecipitationType_Empty", "Day_PrecipitationType_Ice", "Day_PrecipitationType_Mixed",
                             "Day_PrecipitationType_Rain", "Day_PrecipitationType_Snow",
                             "Night_Wind_Direction_Localized_E", "Night_Wind_Direction_Localized_ENE",
                             "Night_Wind_Direction_Localized_ESE", "Night_Wind_Direction_Localized_N",
                             "Night_Wind_Direction_Localized_NE", "Night_Wind_Direction_Localized_NNE",
                             "Night_Wind_Direction_Localized_NNW", "Night_Wind_Direction_Localized_NW",
                             "Night_Wind_Direction_Localized_S", "Night_Wind_Direction_Localized_SE",
                             "Night_Wind_Direction_Localized_SSE", "Night_Wind_Direction_Localized_SSW",
                             "Night_Wind_Direction_Localized_SW", "Night_Wind_Direction_Localized_W",
                             "Night_Wind_Direction_Localized_WNW", "Night_Wind_Direction_Localized_WSW",
                             "Night_WindGust_Direction_Localized_E", "Night_WindGust_Direction_Localized_ENE",
                             "Night_WindGust_Direction_Localized_ESE", "Night_WindGust_Direction_Localized_N",
                             "Night_WindGust_Direction_Localized_NE", "Night_WindGust_Direction_Localized_NNE",
                             "Night_WindGust_Direction_Localized_NNW", "Night_WindGust_Direction_Localized_NW",
                             "Night_WindGust_Direction_Localized_S", "Night_WindGust_Direction_Localized_SE",
                             "Night_WindGust_Direction_Localized_SSE", "Night_WindGust_Direction_Localized_SSW",
                             "Night_WindGust_Direction_Localized_SW", "Night_WindGust_Direction_Localized_W",
                             "Night_WindGust_Direction_Localized_WNW", "Night_WindGust_Direction_Localized_WSW",
                             "Night_PrecipitationType_Empty", "Night_PrecipitationType_Ice",
                             "Night_PrecipitationType_Mixed", "Night_PrecipitationType_Rain",
                             "Night_PrecipitationType_Snow"]
        for col in saved_models_cols:
            if col not in x.columns:
                x[col] = 0

        x_seq, y_seq = self.__create_sequences(x, y)

        if not hasattr(self, 'model') or self.model is None:
            raise ValueError("The model has not yet been trained or loaded.")

        if self.optimizer == 'adam':
            optimizer = Adam(learning_rate=self.learning_rate)
        elif self.optimizer == 'sgd':
            optimizer = tf.keras.optimizers.SGD(learning_rate=self.learning_rate)
        elif self.optimizer == 'rmsprop':
            optimizer = tf.keras.optimizers.RMSprop(learning_rate=self.learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {self.optimizer}")

        self.model.compile(optimizer=optimizer, loss=self.loss, metrics=['mae', 'mse', self.r2_score_keras])
        self.model.fit(x_seq, y_seq, epochs=epochs, batch_size=self.batch_size, verbose=1)

        if save_fine_tuned:
            timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
            filename = f'{self.__class__.__name__}-fine_tuned-{timestamp}.keras'
            self.save_model(filename)
            print(f"The model saved as {filename}.")


class WeatherDataPreprocessor(DataPreprocessor):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.ordinal_columns: list[str] = []

    def preprocess(self, test_size: float = 0.2, pca_components: float = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        self.__preprocess_dates()
        self.__create_useful_columns()
        self.__eliminate_columns()
        self.__encode()
        self.__normalize()
        self.info()

        x_train, x_test, y_train, y_test = self.__separate_data(test_size=test_size)

        if pca_components is not None:
            pca = PCA(n_components=pca_components)
            x_train = pca.fit_transform(x_train)
            x_test = pca.transform(x_test)
            x_train = pd.DataFrame(x_train, columns=[f'PC{i + 1}' for i in range(x_train.shape[1])])
            x_test = pd.DataFrame(x_test, columns=[f'PC{i + 1}' for i in range(x_test.shape[1])])

        return x_train, x_test, y_train, y_test

    def __encode(self):
        # Health Columns
        health_column_names: list[str] = self.data.filter(like='Health_', axis=1).columns.tolist()
        self.data = self.ordinal_encode(health_column_names)
        self.ordinal_columns.extend(health_column_names)

        # Pests Columns
        pests_column_names: list[str] = self.data.filter(like='Pests_', axis=1).columns.tolist()
        self.data = self.ordinal_encode(pests_column_names)
        self.ordinal_columns.extend(pests_column_names)

        # AirAndPollen Columns
        air_and_pollen_column_names: list[str] = self.data.filter(like='AirAndPollen_', axis=1).columns.tolist()
        self.ordinal_columns.extend(air_and_pollen_column_names)
        air_and_pollen_column_names.remove('AirAndPollen_AirQuality')
        self.data = self.ordinal_encode(['AirAndPollen_AirQuality'], ['Bad', 'Good'])
        self.data = self.ordinal_encode(air_and_pollen_column_names)

        # Season
        self.data = self.one_hot_encode(['Season'])

        # Day Columns
        self.data = self.one_hot_encode(['Day_Wind_Direction_Localized', 'Day_WindGust_Direction_Localized', 'Day_PrecipitationType'])
        self.data = self.ordinal_encode(['Day_PrecipitationIntensity'], ['Light', 'Moderate', 'Heavy'])
        self.ordinal_columns.append('Day_PrecipitationIntensity')
        self.data['Day_HasPrecipitation'] = self.data['Day_HasPrecipitation'].astype(int)

        # Night Columns
        self.data = self.one_hot_encode(['Night_Wind_Direction_Localized', 'Night_WindGust_Direction_Localized', 'Night_PrecipitationType'])
        self.data = self.ordinal_encode(['Night_PrecipitationIntensity'], ['Light', 'Moderate', 'Heavy'])
        self.ordinal_columns.append('Night_PrecipitationIntensity')
        self.data['Night_HasPrecipitation'] = self.data['Night_HasPrecipitation'].astype(int)

    def __eliminate_columns(self):
        # OutdoorActivities Columns
        outdoor_activities_column_names: list[str] = self.data.filter(like='OutdoorActivities_',
                                                                      axis=1).columns.tolist()
        self.data.drop(columns=outdoor_activities_column_names, inplace=True)

        # TravelAndCommute Columns
        travel_and_commute_column_names: list[str] = self.data.filter(like='TravelAndCommute_', axis=1).columns.tolist()
        self.data.drop(columns=travel_and_commute_column_names, inplace=True)

        # HomeAndGarden Columns
        home_and_garden_column_names: list[str] = self.data.filter(like='HomeAndGarden_', axis=1).columns.tolist()
        self.data.drop(columns=home_and_garden_column_names, inplace=True)

        # City and District
        self.data.drop(columns=['City', 'District'], inplace=True)

        # Moon Columns
        moon_column_names: list[str] = self.data.filter(like='Moon_', axis=1).columns.tolist()
        self.data.drop(columns=moon_column_names, inplace=True)

        # Temperature Columns
        self.data.drop(columns=['RealFeelTemperature_Minimum_Phrase', 'RealFeelTemperature_Maximum_Phrase',
                                'RealFeelTemperatureShade_Minimum_Phrase',
                                'RealFeelTemperatureShade_Maximum_Phrase', 'DegreeDaySummary_Heating_Value',
                                'DegreeDaySummary_Cooling_Value'], inplace=True)

        # Day Columns
        self.data.drop(columns=['Day_IconPhrase', 'Day_ShortPhrase', 'Day_LongPhrase'],
                       inplace=True)  # Undecided about Day_IconPhrase.

        # Night Columns
        self.data.drop(columns=['Night_IconPhrase', 'Night_ShortPhrase', 'Night_LongPhrase'],
                       inplace=True)  # Undecided about Night_IconPhrase.

        # CityId and DistrictId Columns
        #self.data.drop(columns=['CityId', 'DistrictId'], inplace=True)

    def __preprocess_dates(self):
        # Date
        self.data['Year'] = self.data['Date'].dt.year
        self.data['Month'] = self.data['Date'].dt.month
        self.data['Day'] = self.data['Date'].dt.day
        self.data['Hour'] = self.data['Date'].dt.hour
        self.data['DayOfYear'] = self.data['Date'].dt.dayofyear
        self.data['DayOfYearRatio'] = self.data['DayOfYear'] / 365.0
        self.data.drop(columns=['Date', 'DayOfYear'], inplace=True)

        # Sun Columns
        sun_column_names: list[str] = self.data.filter(like='Sun_', axis=1).columns.tolist()
        self.data[sun_column_names] = self.data[sun_column_names].apply(pd.to_datetime)
        self.data['Sun_Rise_Hour'] = self.data['Sun_Rise'].dt.hour
        self.data['Sun_Rise_Minute'] = self.data['Sun_Rise'].dt.minute
        self.data['Sun_Set_Hour'] = self.data['Sun_Set'].dt.hour
        self.data['Sun_Set_Minute'] = self.data['Sun_Set'].dt.minute
        self.data.drop(columns=sun_column_names, inplace=True)

    def __create_useful_columns(self):
        # CityRegion Column
        cities = City.objects.all().values('id', 'region_id')
        cities = pd.DataFrame(list(cities))
        self.data = self.data.merge(cities[['id', 'region_id']], left_on='CityId', right_on='id', how='left')
        self.data['CityRegion'] = self.data['region_id']
        self.data.drop(columns=['id', 'region_id'], inplace=True)

    def __normalize(self):
        one_hot_columns = [col for col in self.data.columns if set(self.data[col].unique()) <= {0, 1}]
        numeric_columns = [col for col in self.data.columns if
                           col not in self.ordinal_columns and col not in one_hot_columns and
                           pd.api.types.is_numeric_dtype(self.data[col])]

        scaler = MinMaxScaler()
        self.data[numeric_columns] = scaler.fit_transform(self.data[numeric_columns])

    def __separate_data(self, test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        columns_to_predict = self.data.filter(like='AirAndPollen', axis=1).copy()
        columns_to_predict.drop(columns=['AirAndPollen_UVIndex', 'AirAndPollen_AirQuality'], inplace=True)
        target = columns_to_predict.copy()
        self.data.drop(columns=columns_to_predict.columns, inplace=True)

        split_index = int(len(self.data) * (1 - test_size))
        x_train = self.data.iloc[:split_index]
        x_test = self.data.iloc[split_index:]
        y_train = target.iloc[:split_index]
        y_test = target.iloc[split_index:]
        return x_train, x_test, y_train, y_test
