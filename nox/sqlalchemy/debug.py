# -*- coding: utf8 -*-
#
# nox - Copyright (C) nox contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

'''The ``nox.sqlalchemy.debug`` packages contains get_compiled_query'''

import sqlalchemy.orm
import datetime

def get_compiled_query(statement, bind = None):
    '''
    Get a query like if it was written literally.
    For debugging purposes *only*, for security, you should always separate queries from their values.

    Credits to (bukzor and vvladymyrov): http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query

    :param statement: query statement
    :param bind: bind from session (default: None - get it from statement)
    :return: query string
    '''

    if isinstance(statement, sqlalchemy.orm.Query):
        if bind is None:
            bind = statement.session.get_bind(
                statement._mapper_zero_or_none()
            )
        statement = statement.statement
    elif bind is None:
        bind = statement.bind

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(
                self, bindparam, within_columns_clause = False,
                literal_binds = False, **kwargs
        ):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause = within_columns_clause,
                literal_binds = literal_binds, **kwargs
            )

        def render_literal_value(self, value, type_):
            if isinstance(value, datetime.datetime):
                return "TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')" % value.strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(value, '__call__'):
                return str(value())
            else:
                return super(LiteralCompiler, self).render_literal_value(value, type_)

    compiler = LiteralCompiler(dialect, statement)
    return compiler.process(statement)
