%module swig_nufft 
%{
#define SWIG_FILE_WITH_INIT
int fourier_interpolate_3d(float *v, int dim1, int n1, int n2, int n3, double *x, int dim2, float *res, int dim3);
int fourier_rotate_vol(float *v, int dim1, int n1, int n2, int n3, double *rot, int dim2, float *res, int dim3);
%}
%include "numpy.i"
%init %{
    import_array();
%}

int fourier_interpolate_3d(float *IN_ARRAY1, int DIM1, int n1, int n2, int n3, double *IN_ARRAY1, int DIM1, float *INPLACE_ARRAY1, int DIM1);

int fourier_rotate_vol(float *IN_ARRAY1, int DIM1, int n1, int n2, int n3, double *IN_ARRAY1, int DIM1, float *INPLACE_ARRAY1, int DIM1);