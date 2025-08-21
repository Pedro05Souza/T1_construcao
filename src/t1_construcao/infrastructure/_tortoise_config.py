from t1_construcao.shared import get_env_var

__all__ = ["TORTOISE_ORM"]

TORTOISE_ORM = {
    "connections": {"default": get_env_var("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["t1_construcao.infrastructure.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
