from pydantic import BaseSettings, Field
from db.dsn import generate_dsn_postgres


class Settings(BaseSettings):
    DB_USERNAME: str = Field(env='POSTGRES_USER',)
    DB_PASSWORD: str = Field(env="POSTGRES_PASSWORD",)
    DB_PORT: int = Field(env='POSTGRES_PORT',)
    DB_HOST: str = Field(env='POSTGRES_HOST',)
    DB_BASENAME: str = Field(env='POSTGRES_DB',)
    TG_TOKEN: str = Field(env='TG_TOKEN')

    @property
    def dsn(self):
        return generate_dsn_postgres(
            user=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database_name=self.DB_BASENAME
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings_app = Settings()
