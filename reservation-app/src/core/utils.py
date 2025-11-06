"""Utils for core module."""


def get_env_file_path(env_file_names: list[str]) -> list[str]:
    """
    Get environment file paths from environment file names.

    :param env_file_names: List of environment file names.

    :return List[str]: Environment file paths.
    """
    path_prefix: str = "../../"
    return [f"{path_prefix}{env_file}" for env_file in env_file_names]
