"""Utils for core module."""
from typing import List
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import CreateTable
from sqlalchemy.sql.compiler import DDLCompiler


def get_env_file_path(env_file_names: List[str]) -> List[str]:
    """Get environment file paths from environment file names.

    :param env_file_names: List of environment file names.

    :return List[str]: Environment file paths.
    """
    path_prefix: str = "../"
    return [f"{path_prefix}{env_file}" for env_file in env_file_names]


@compiles(CreateTable)
def compile_create_table(element, compiler: DDLCompiler, **kwargs) -> str:
    """
    Custom compilation for CREATE TABLE statement.
    This function is used to customize how CREATE TABLE statements are compiled into SQL.

    :param element: The CreateTable object to compile.
    :param compiler: The DDLCompiler used to generate the SQL.
    :param kwargs: Additional keyword arguments.
    :return: The compiled SQL statement as a string.
    """
    if not isinstance(compiler, DDLCompiler):
        raise TypeError("Compiler should be an instance of DDLCompiler")

    # Compile the SQL using the provided compiler
    text = compiler.visit_create_table(element, **kwargs)

    # Replace 'SERIAL' with 'INTEGER' for compatibility with DuckDB
    text = text.replace("SERIAL", "INTEGER")

    return text
