import swig_nufft
import numpy as np

def fourier_interpolate_3d_vol(v, nodes):
	"""Given a real 3D volume data in PyTom format, interpolate at specified locations in Fourier space.
	@param v: 3D volume data in PyTom format.
	@dtype v: Pytom_volume.vol
	@param nodes: a list of locations in Fourier space. Each node must be in the range [-0.5, 0.5).
	@dtype nodes: List. [[-0.5, -0.5, 0.3], ...]
	@return: interpolated complex values in a list.
	@rtype: List.
	"""
	from pytom_numpy import vol2npy

	# convert to numpy format
	v = vol2npy(v)
	dim_x, dim_y, dim_z = v.shape

	# shift it
	v = np.fft.fftshift(v)

	# linearize it
	v = v.reshape((v.size))

	# linearize it
	nodes = np.array(nodes, dtype="double")
	nodes = nodes.reshape((nodes.size))

	# call the function
	res = fourier_interpolate_3d(v, dim_x, dim_y, dim_z, nodes, nodes.size/3)

	# convert to complex format
	res = res[::2] + 1j*res[1::2]

	return res

def fourier_interpolate_3d(v, dim_x, dim_y, dim_z, nodes, num_nodes):
	"""Wrapper to the low level c function. Should not be used directly.
	@param v: linearized 3D volume data in numpy format.
	@dtype v: numpy.array
	@param dim_x:
	"""
	if v.__class__ != np.ndarray or nodes.__class__ != np.ndarray:
		raise RuntimeError("Input args must have numpy.ndarray type!")
	
	# allocate the result memory
	res = np.zeros(num_nodes*2, dtype="float32")

	swig_nufft.fourier_interpolate_3d(v, dim_x, dim_y, dim_z, nodes, res)

	return res

def fourier_rotate_vol(v, angle):
	"""Be careful with rotating a odd-sized volume, since nfft will not give correct result!
	"""
	# get the rotation matrix
	from pytom.basic.structures import Rotation
	rot = Rotation(angle)
	m = rot.toMatrix()
	m = m.transpose() # get the invert rotation matrix
	m = np.array([m.getRow(0), m.getRow(1), m.getRow(2)], dtype="float32")
	m = m.flatten()

	# prepare the volume
	from pytom_numpy import vol2npy

	v = vol2npy(v)
	dim_x, dim_y, dim_z = v.shape

	# twice shift means no shift!
	# v = np.fft.fftshift(v)

	# linearize it
	v = v.reshape((v.size))

	# allocate the memory for the result
	res = np.zeros(v.size*2, dtype="float32")

	# call the low level c function
	swig_nufft.fourier_rotate_vol(v, dim_x, dim_y, dim_z, m, res)

	res = res[::2] + 1j*res[1::2]
	res = res.reshape((dim_x, dim_y, dim_z), order='F')

	# inverse fft
	ans = np.fft.ifftshift(np.real(np.fft.ifftn(np.fft.ifftshift(res))))

	# transfer to pytom volume format
	from sh.frm import np2vol
	res = np2vol(ans)

	return res

def node2index(node, size):
	if node < -0.5 or node >= 0.5:
		raise RuntimeError("Node should be in [-0.5, 0.5) !")

	return int(node*size+size/2)

def index2node(index, size):
	if index < 0 or index > size:
		raise RuntimeError("Index should be in range [0, size] !")

	return float(index)/size - 0.5

def node2index_3d(node, size):
	if size.__class__ == int:
		size = [size, size, size]
	elif size.__class__ == list:
		pass
	else:
		raise RuntimeError("Size must be an int or list!")

	return [node2index(node[0], size[0]), node2index(node[1], size[1]), node2index(node[2], size[2])]

def index2node_3d(index, size):
	if size.__class__ == int:
		size = [size, size, size]
	elif size.__class__ == list:
		pass
	else:
		raise RuntimeError("Size must be an int or list!")

	return [index2node(index[0], size[0]), index2node(index[1], size[1]), index2node(index[2], size[2])]

def get_nodes(r, size, b):
    """Get the nodes in NFFT format
    """
    from math import pi, cos, sin

    res = []
    for j in xrange(2*b):
        for k in xrange(2*b):
            the = pi*(2*j+1)/(4*b) # (0,pi)
            phi = pi*k/b # [0,2*pi)
            res.append([r*cos(phi)*sin(the)/size, r*sin(phi)*sin(the)/size, r*cos(the)/size])

    return res