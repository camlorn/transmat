from make_cffi import *
from .polar import * #the helper function for unit vectors in specific directions.
from .conf import *

def compare_vectors(v1, v2):
	for i, j in zip(v1, v2):
		assert abs(i-j) < accuracy

def setMatrix(mat, l):
	for i, j in enumerate(l):
		mat[i%4][i/4] = j

def test_transform_identity():
	trans = ffi.new("TmTransform*")
	transmat.Tm_identityTransform(trans)
	vec = ffi.new("TmVector*")
	vec.vec = (5, 10, 20)
	out = ffi.new("TmVector*")
	transmat.Tm_transformApply(trans[0], vec[0], out)
	compare_vectors(vec.vec, out.vec)

def test_transform_invert_orthoganal():
	trans = [ffi.new("TmTransform*"), ffi.new("TmTransform*"), ffi.new("TmTransform*"), ffi.new("TmTransform*")]
	inv = [ffi.new("TmTransform*"), ffi.new("TmTransform*"), ffi.new("TmTransform*"), ffi.new("TmTransform*")]
	#we need a source of known orthoganal matrices.
	#we thus use the camera function.
	#it'll work so long as it returns something orthoganal, even if it fails its test.
	at1, up1, pos1 = ffi.new("TmVector*"), ffi.new("TmVector*"), ffi.new("TmVector*")
	at2, up2, pos2 = ffi.new("TmVector*"), ffi.new("TmVector*"), ffi.new("TmVector*")
	at3, up3, pos3 = ffi.new("TmVector*"), ffi.new("TmVector*"), ffi.new("TmVector*")
	at1.vec, up1.vec, pos1.vec = direct(0, -45), direct(0, 45), [5, -30, 0, 1]
	at2.vec, up2.vec, pos2.vec = direct(45, 0), direct(45, 90), [0, 0, 0, 1]
	at3.vec, up3.vec, pos3.vec = direct(0, -0), direct(0, -90), [0, 0, 0, 1]
	transmat.Tm_cameraTransform(at1[0], up1[0], pos1[0], trans[0])
	transmat.Tm_cameraTransform(at2[0], up2[0], pos2[0], trans[1])
	transmat.Tm_cameraTransform(at3[0], up3[0], pos3[0], trans[2])
	transmat.Tm_identityTransform(trans[3])
	trans[3].mat[0][3] = 5
	trans[3].mat[1][3] = 22
	trans[3].mat[2][3] = -13
	for i, j in enumerate(trans):
		transmat.Tm_transformInvertOrthoganal(j[0], inv[i])
	for i, j in zip(trans, inv):
		input = ffi.new("TmVector*")
		output = ffi.new("TmVector*")
		input.vec = [0.5, 0.5, 0.5, 1]
		output.vec = [0, 0, 0, 1]
		transmat.Tm_transformApply(i[0], input[0], output)
		transmat.Tm_transformApply(j[0], output[0], output)
		compare_vectors(input.vec, output.vec)

def test_transform_camera():
	trans = ffi.new("TmTransform*")
	at, up, pos = ffi.new("TmVector*"), ffi.new("TmVector*"), ffi.new("TmVector*")
	at.vec, up.vec, pos.vec = direct(0, -30), direct(0, 60), [0, 0, 0, 0]
	transmat.Tm_cameraTransform(at[0], up[0], pos[0], trans)
	#we have a camera looking east and down a bit, so that the x axis of the world is angled upward, the y axis is tilted back, and the z axis is to our right.
	#first, a vector that points directly to the right of the camera.  In this case, the positive z direction.
	out = ffi.new("TmVector*")
	#this is directly to the right of the camera as it is oriented in 3d space:
	right = ffi.new("TmVector*")
	right.vec = [0, 0, 1, 1]
	transmat.Tm_transformApply(trans[0], right[0], out)
	#it should yield the positive x axis in camera space.
	compare_vectors([1, 0, 0, 1], out.vec)
	#a vector directed in the same direction as the camera should yield the z axis:
	forward = ffi.new("TmVector*")
	forward.vec = direct(0, -30)
	transmat.Tm_transformApply(trans[0], forward[0], out)
	compare_vectors([0, 00, -1, 1], out.vec)
	#and a vector in the up direction must give y.
	up = ffi.new("TmVector*")
	up.vec = direct(0, 60)
	transmat.Tm_transformApply(trans[0], up[0], out)
	compare_vectors([0, 1, 0, 1], out.vec)
	#this next bit tests translation.
	offset = [10, 5, 13, 0]
	at.vec, up.vec, pos.vec = direct(0, -30), direct(0, 60), offset
	transmat.Tm_cameraTransform(at[0], up[0], pos[0], trans)
	#in order for this to work, we have to pointwise add in our translation to the world coordinate test vectors.
	#otherwise, it's identical.
	expected_z = [i+j for i, j in zip(direct(0, -30), offset)]
	expected_y = [i+j for i, j in zip(direct(0, 60), offset)]
	expected_x = [i+j for i, j in zip([0, 0, 1, 1], offset)]
	expected_xv, expected_yv, expected_zv = ffi.new("TmVector*"), ffi.new("TmVector*"), ffi.new("TmVector*")
	expected_xv.vec, expected_yv.vec, expected_zv.vec = expected_x, expected_y, expected_z
	transmat.Tm_transformApply(trans[0], expected_xv[0], out)
	compare_vectors([1, 0, 0, 1], out.vec)
	transmat.Tm_transformApply(trans[0], expected_yv[0], out)
	compare_vectors([0, 1, 0, 1], out.vec)
	transmat.Tm_transformApply(trans[0], expected_zv[0], out)
	compare_vectors([0, 0, -1, 1], out.vec)
