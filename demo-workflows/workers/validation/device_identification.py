from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow import fields
from marshmallow import validates


VALID_PORT_START = ("10", "17")


class DeviceIdentificationSchema(Schema):
    port = fields.Int(required=True)

    @validates("port")
    def validate_port_input(self, port: str) -> None:
        if not port:
            raise ValidationError("Please input port")

        try:
            port = int(port)
        except:
            raise ValidationError("Port must be integer")

        if not str(port).startswith(VALID_PORT_START):
            raise ValidationError(f"Port must begin with one of these numbers {VALID_PORT_START}. for ex. 10001,17100")


