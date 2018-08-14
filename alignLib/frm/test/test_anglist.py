"""
Test the angle list used in template matching to see if the angluar distance is actually consistent with the file name.
"""

from pytom.tools.maths import rotation_distance
from pytom.angles.fromFile import AngleListFromEM
ang = AngleListFromEM('angles_07_45123.em')
# ang = AngleListFromEM('angles_12.85_7112.em')

from eulerDist import distEuler

for i in xrange(len(ang)-1):
	a1 = ang[i]
	a2 = ang[i+1]

	if rotation_distance(a1, a2)-distEuler(a1, a2) > 0.1:
		print a1, a2, rotation_distance(a1, a2)-distEuler(a1, a2)
