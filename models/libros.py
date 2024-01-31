# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Fichero abstracto'

    activo = fields.Boolean(default=True)

    def archivar(self):
        for record in self:
            record.activo = not record.activo

class Libro(models.Model):
    _name = 'libro'
    _inherit = ['base.archive']
    _description = 'Libros'
    _order = 'fecha_publicacion desc, nombre'

    _rec_name = 'nombre'

    nombre = fields.Char('Titulo', required=True, index=True)
    
    descripcion = fields.Html('Descripción', sanitize=True, strip_style=False)

    portada = fields.Binary('Portada Libro')

    fecha_publicacion = fields.Date('Fecha publicación')

    paginas = fields.Integer('Numero de páginas',
        groups='base.group_user',
        estados={'perdido': [('readonly', True)]},
        help='Total numero de paginas',
        company_dependent=False)

    autor_ids = fields.Many2many('libro.autor')

    saga_id = fields.Many2one('libro.saga')
    
    dias_lanzamiento = fields.Integer(
        string='Dias desde lanzamiento',
        compute='_compute_anyo', inverse='_inverse_anyo', search='_search_anyo',
        store=False,
        compute_sudo=True,
    )

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('fecha_publicacion')
    def _compute_anyo(self):
        hoy = fields.Date.today()
        for libro in self:
            if libro.fecha_publicacion:
                delta = hoy - libro.fecha_publicacion
                libro.dias_lanzamiento = delta.days
            else:
                libro.dias_lanzamiento = 0


    def _inverse_anyo(self):
        hoy = fields.Date.today()
        for libro in self.filtered('fecha_publicacion'):
            d = hoy - timedelta(days=libro.dias_lanzamiento)
            libro.fecha_publicacion = d

    def _search_age(self, operator, value):
        hoy = fields.Date.today()
        value_dias = timedelta(dias=value)
        value_fecha = hoy - value_dias
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('fecha_publicacion', new_op, value_fecha)]

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.nombre, record.fecha_publicacion)
            result.append((record.id, rec_name))
        return result

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (nombre)', 'El titulo Comic debe ser único.'),
        ('positive_page', 'CHECK(paginas>0)', 'El comic debe tener al menos una página')
    ]

    @api.constrains('fecha_publicacion')
    def _check_release_date(self):
        for record in self:
            if record.fecha_publicacion and record.fecha_publicacion > fields.Date.today():
                raise models.ValidationError('La fecha de lanzamiento debe ser anterior a la actual')