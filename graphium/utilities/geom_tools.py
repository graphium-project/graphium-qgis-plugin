from qgis.core import (QgsProject, QgsDistanceArea, QgsPointXY, QgsGeometryUtils)
import datetime


class GeomTools:
    def __init__(self):
        pass

    @staticmethod
    def is_equal_coordinate(point_a, point_b):
        return point_a.x() == point_b.x() and point_a.y() == point_b.y()

    @staticmethod
    def calculate_speed(time_a, time_b, point_a, point_b, crs):
        distance = GeomTools.distance(point_a, point_b, crs)

        time_diff_h = GeomTools.calculate_duration(time_a, time_b)
        if time_diff_h > 0:
            return float((distance / 1000) / (time_diff_h / 3600))
        else:
            return None

    @staticmethod
    def calculate_duration(time_a, time_b):
        if type(time_a) is datetime.datetime:  # TODO only use one type of date
            duration = (time_b - time_a).total_seconds()
        else:
            duration = time_a.msecsTo(time_b) / 1000
        return duration

    @staticmethod
    def distance(start, end, crs):
        distance = QgsDistanceArea()
        # distance.setEllipsoidalMode(True)
        if crs is not None:
            distance.setSourceCrs(crs, QgsProject.instance().transformContext())
            if distance.sourceCrs().isGeographic():
                distance.setEllipsoid(distance.sourceCrs().ellipsoidAcronym())
        else:
            distance.setEllipsoid('WGS84')
        return distance.measureLine(QgsPointXY(start), QgsPointXY(end))

    @staticmethod
    def calculate_angle(point_a, point_b):
        return QgsGeometryUtils.lineAngle(point_a.x(), point_a.y(), point_b.x(), point_b.y())
