import typing
from typing import List, Optional

from sqlalchemy.engine.reflection import Inspector

from datahub.ingestion.source.sql.sql_common import (
    SQLAlchemyConfig,
    SQLAlchemySource,
    make_sqlalchemy_uri,
)


class AthenaConfig(SQLAlchemyConfig):
    scheme: str = "awsathena+rest"
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    aws_region: str
    s3_staging_dir: str
    work_group: str

    include_views = False  # not supported for Athena

    def get_sql_alchemy_url(self):
        return make_sqlalchemy_uri(
            self.scheme,
            self.username or "",
            self.password,
            f"athena.{self.aws_region}.amazonaws.com:443",
            self.database,
            uri_opts={
                "s3_staging_dir": self.s3_staging_dir,
                "work_group": self.work_group,
            },
        )


class AthenaSource(SQLAlchemySource):
    def __init__(self, config, ctx):
        super().__init__(config, ctx, "athena")

    @classmethod
    def create(cls, config_dict, ctx):
        config = AthenaConfig.parse_obj(config_dict)
        return cls(config, ctx)

    # It seems like database/schema filter in the connection string does not work and this to work around that
    def get_schema_names(self, inspector: Inspector) -> List[str]:
        athena_config = typing.cast(AthenaConfig, self.config)
        schemas = inspector.get_schema_names()
        if athena_config.database:
            return [schema for schema in schemas if schema == athena_config.database]
        return schemas
