from odoo import models, fields


class Room(models.Model):
    _name = "sisi.room"
    _description = "Room Definition & Management"
    _rec_name = "room_no"

    room_no = fields.Char(string="Room Number", required=True)
    type = fields.Selection(
        [("classroom", "Classroom"),
         ("laboratory", "Laboratory"),
         ("office", "Office"),
         ("hall", "Hall"),
         ("library", "Library"),
         ("na", "NA")], )

    max_capacity = fields.Integer(string="Maximum Capacity", default=0)

    school_id = fields.Many2one(
        comodel_name="sisi.school",
        string="School",
        ondelete="set null",
        help='Select the school this room belongs to')

    _sql_constraints = [
        ('room_no_unique', 'unique(room_no, school_id)', 'Room number must be unique within the same school.'),
    ]
