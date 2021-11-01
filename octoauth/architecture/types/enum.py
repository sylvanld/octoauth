class StringEnum(str):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield None

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            enum=[getattr(cls, attr) for attr in dir(cls) if attr.isupper()],
        )
