# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonSquarer
                                 A QGIS plugin
 Least square algorithm
                             -------------------
        begin                : 2018-05-22
        copyright            : (C) 2018 by Imran
        email                : imran.lokhat@ign.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PolygonSquarer class from file PolygonSquarer.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .polygon_squarer import PolygonSquarer
    return PolygonSquarer(iface)
