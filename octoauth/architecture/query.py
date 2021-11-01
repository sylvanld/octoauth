import inspect
from typing import Any, Optional

import sqlalchemy
from fastapi import Query


def column_type_in(column_types: set, sqlalchemy_column: sqlalchemy.Column):
    for column_type in column_types:
        if isinstance(sqlalchemy_column.type, column_type):
            return True
    return False


class Filters(list):
    ...


class FiltersBuilder:
    def __init__(builder):
        builder.filter_generators = []

    def add_equals_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _equals_filter(query_params: dict):
            if query_params.get(query_param):
                return column == query_params[query_param]

        builder.filter_generators.append(_equals_filter)
        return builder

    def add_min_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _min_filter(query_params: dict):
            if query_params.get(query_param):
                return column >= query_params[query_param]

        builder.filter_generators.append(_min_filter)
        return builder

    def add_max_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _max_filter(query_params: dict):
            if query_params.get(query_param):
                return column <= query_params[query_param]

        builder.filter_generators.append(_max_filter)
        return builder

    def add_startswith_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _startswith_filter(query_params: dict):
            if query_params.get(query_param):
                return column.startswith(query_params[query_param])

        builder.filter_generators.append(_startswith_filter)
        return builder

    def add_endswith_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _endswith_filter(query_params: dict):
            if query_params.get(query_param):
                return column.endswith(query_params[query_param])

        builder.filter_generators.append(_endswith_filter)
        return builder

    def add_contains_filter(builder, query_param: str, column: sqlalchemy.Column):
        def _contains_filter(query_params: dict):
            if query_params.get(query_param):
                return column.contains(query_params[query_param])

        builder.filter_generators.append(_contains_filter)
        return builder

    def get_filters(builder, query_params: dict) -> Filters:
        filters = Filters()
        for generator in builder.filter_generators:
            filter_ = generator(query_params)
            if filter_ is not None:
                filters.append(filter_)
        return filters


COMPARABLE_COLUMNS = {
    sqlalchemy.Float,
    sqlalchemy.Integer,
    sqlalchemy.DateTime,
    sqlalchemy.Date,
    sqlalchemy.Time,
}
TEXTUAL_COLUMNS = {sqlalchemy.String}


class QueryParserBuilder:
    def __init__(builder):
        builder.query_params = []
        builder.filters_builder = FiltersBuilder()

    def add_query_param(self, parameter_name: str, parameter_type: Any):
        self.query_params.append(
            inspect.Parameter(
                parameter_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=Query(None, alias=parameter_name.replace("_", "-")),
                annotation=Optional[parameter_type],
            )
        )

    def enable_equals_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = sqlalchemy_column.name
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_equals_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_min_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = f"min_{sqlalchemy_column.name}"
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_min_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_max_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = f"max_{sqlalchemy_column.name}"
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_max_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_startswith_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = f"{sqlalchemy_column.name}_startswith"
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_startswith_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_endswith_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = f"{sqlalchemy_column.name}_endswith"
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_endswith_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_contains_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        parameter_name = f"{sqlalchemy_column.name}_contains"
        builder.add_query_param(parameter_name, sqlalchemy_column.type.python_type)
        builder.filters_builder.add_contains_filter(parameter_name, sqlalchemy_column)
        return builder

    def enable_full_filtering_on(builder, sqlalchemy_column: sqlalchemy.Column):
        # equals filtering is valid for any kind of column
        builder.enable_equals_filtering_on(sqlalchemy_column)

        # min/max filtering are suitable for numbers and dates columns
        if column_type_in(
            COMPARABLE_COLUMNS,
            sqlalchemy_column,
        ):
            builder.enable_min_filtering_on(sqlalchemy_column)
            builder.enable_max_filtering_on(sqlalchemy_column)

        if column_type_in(TEXTUAL_COLUMNS, sqlalchemy_column):
            builder.enable_contains_filtering_on(sqlalchemy_column)
            builder.enable_startswith_filtering_on(sqlalchemy_column)
            builder.enable_endswith_filtering_on(sqlalchemy_column)

        return builder

    def build(builder):
        def query_parser(**query_params) -> Filters:
            return builder.filters_builder.get_filters(query_params)

        query_parser.__signature__ = inspect.Signature(parameters=builder.query_params)
        return query_parser
