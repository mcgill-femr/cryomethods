/*********************************************************************
 *                           FRM VOLUMETRIC   2/20/03                *
 **********************************************************************
 * Program is part of the Situs package URL: http://situs.scripps.edu *
 * (c) Julio Kovacs, Pablo Chacon and Willy Wriggers, 2001-2002       *
 **********************************************************************
 *                                                                    *
 * General volumetric accelerated rotational fitting tool.            * 
 *                                                                    *
 **********************************************************************
 * Due to the use of the FFTW library we are forced to distribute     *
 * this file under the GNU General Public License (GPL) appended to   *
 * the source code below. The GNU GPL license replaces the legal      *
 * statement distributed with the Situs package.                      *
 *********************************************************************/


#include "situs.h"
#include <fftw.h>
#define SQT2 sqrt(2.0)


/* global variables */
static double g_target_res;                  /* resolution in A */
static double g_low_cutoff;                  /* low res. map cutoff */
static double g_high_cutoff;                 /* high res. map cutoff */
static unsigned g_extx;                      /* map extent */
static unsigned g_exty;                      /* map extent */
static unsigned g_extz;                      /* map extent */
static unsigned long g_nvox;                 /* number of voxels */
static double g_width;                       /* voxel size in Angstroms */
static double g_gridx;                       /* map origin */
static double g_gridy;                       /* map origin */
static double g_gridz;                       /* map origin */
static double *g_phi_lo;         	     /* low resolution map */
static double *g_phi_hi;		     /* high resolution map */
static double *g_phi_du;	             /* dummy map */
static double *g_phi_ga;                     /* low-pass (Gaussian) kernel */
static unsigned g_ext_ga;                    /* low-pass kernel linear extent*/
static unsigned long g_nvox_ga;              /* low-pass kernel voxel count */
static unsigned g_num_atoms;                 /* number of PDB atoms */

static PDB *g_pdb_original;                  /* PDB coordinates */
static PDB *g_pdb_move;                      /* dummy PDB coordinates */
static unsigned g_num_explored;              /* number of explored best fits */

/* external general funtions from libraries */
extern void zero_vect (double *, unsigned long);
extern void do_vect (double **, unsigned long);
extern void cp_vect (double **, double **, unsigned long);
extern void cp_vect_destroy (double **, double **, unsigned long);
extern void create_padded_map (double **, unsigned *, unsigned *, unsigned *, double *, double *, 
			       double *, unsigned long *, double *, unsigned, unsigned, unsigned, 
			       double, double, double, double, double, double, unsigned *);

extern unsigned long gidz_general (int, int, int, unsigned, unsigned);
extern void shrink_margin (double **, unsigned *, unsigned *, unsigned *, double *, double *, 
			   double *, unsigned long *, double *, unsigned, unsigned, unsigned, 
			   double, double, double, double);
extern void threshold (double *, unsigned long, double);
extern void readvol (char *, double *, double *, double *, double *, int *, int *, int *, double **);
extern void writevol (char *, double, double, double, double, int, int, int, double *);
extern void print_map_info (double *, unsigned long);
extern double calc_mass (PDB *, unsigned); 
extern double calc_center_mass (PDB *, unsigned, double *, double *, double *);

extern void create_gaussian (double **, unsigned long *, unsigned *, double, double);
extern void convolve_kernel_inside (double **, double *, unsigned, unsigned, unsigned, double *, unsigned);  

extern void project_mass (double **, unsigned long, double, double, double, 
			  unsigned, unsigned, unsigned, PDB *, unsigned, double *);


extern the_time get_the_time (void);
extern the_time time_diff (the_time, the_time);
extern char *smart_sprint_time (double);
extern double time_to_sec (the_time);

extern double calc_sphere (PDB *, unsigned, double, double, double);
extern void rot_euler (PDB *, PDB *, unsigned, double, double, double);
extern void get_rot_matrix (double [3][3], double, double, double);
extern void translate (PDB *, PDB *, unsigned, double, double, double);
extern void appendpdb (char *, int, PDB *);
extern void read_and_weight_mass (char *, unsigned *, PDB **); 

/* functions defined inn this file */
static void read_options (int,char **);
static void get_centered_structure_and_radius (char *,double *);
static void get_lowmap(char *);
static void get_highmap(char *);
static void draw_line ();
static void cen_of_mass(double *, double *, double *, double *);
static double longitude(int, int);
static double latitude(int, int);
static void wigner(int, double, double *);
static int prime(int, int);
static double distance_eulers(unsigned long, unsigned long, double *[]);
extern int seanindex(int, int, int);

static void fourier_corr(int, double *, double *, double *, double *);
static void volumetric_sampling(double *, double, double, double, double *[], int, int *, int);


main(int argc, char **argv){
  
  /* timers */
  the_time itime, etime;
  the_time time00, time01, time02, time03, time04, time05, time06, time07, time08, time09, time10, time11; 

  double struct_max_radius; 
  double sigma1d;           /* sigma of the Gaussian used for blurring */
  double zero_shift[3] = {0.0, 0.0, 0.0};
  int zeropad[3] = {0, 0, 0};
  double grid_extent_pdb;
  char out_string[20];

  double max_dens_hi, max_dens_lo;        /* maximum densities */
  long i, j, k, l, m,  ind1, ind2, ind3, size2;
  long ncorr, npeaks;
  int nfits=20;             /* number of best fits to be output */

  double comx_hi, comy_hi, comz_hi;  /* center of mass of high res. map */
  double comx_lo, comy_lo, comz_lo;  /* center of mass of low res. map */

  int log2s;       /* log2 of size */
  int bw;          /* bandwidth for sampling on the sphere */
  int size;        /* no. of points in each coordinate = 2*bw */
  int cut_naive;   /* switch from semi-naive to naive at order bw - cut_naive */
  
  fftwnd_plan plan_fftw;     /* plan for the FFTW routine */
  
  double temp, tempi, tempj, tempk;
  double f000, f100, f200, f010, f020, f001, f002;

  double phi, th, psi;        /* Euler angles */
  double phe, phc, ohm;       /* angular parameters */

  double dist_cut;            /* cutoff distance for eliminating nearby peaks */

  double *seminaive_naive_tablespace, *workspace;
  double **seminaive_naive_table;

  double *idata;              /* imaginary data (0) */

  double *coeffr_hi, *coeffi_hi;  /* spherical harmonics coefficients for high res. map */
  double *coeffr_lo, *coeffi_lo;  /* spherical harmonics coefficients for low res. map */

  double *ddd;        /* piramid array for the d-functions */

  double *coef_corr;        /* Fourier coefficients of correlation function */

  double *corr[4];    /* correlation peaks and corresponding Euler angles */


  int rmax_dens_hi, rmax_dens_lo;  /* maximum r's for the high and low res maps (sampling is 0 for r>rmax)*/
  int rmaxm;         /* smaller of rmax_dens_hi, rmax_dens_lo */

  int r,init;
  long tl,r2,index;
  
  double **sph_sampl_lo;  /* array that will contain samplings of the low res. map */
                          /* [0] corresponds to r=0, [1] to r=1 and so on */
  double **sph_sampl_hi;  /* array that will contain samplings of the high res. map */
                          /* [0] corresponds to r=0, [1] to r=1 and so on */
  
  double *integralr;      /* real part of integrals with respect to r of the spherical coefficients */
                          /* (pyramid array like ddd) */
  double *integrali;      /* imag part of integrals with respect to r of the spherical coefficients */
                          /* (pyramid array like ddd) */

  int  max_r;       /* maximum number of r values for the sampling the densities, minus 1 */


  /* ============== INITIALIZATION =====================*/ 
 
  itime = get_the_time();
  
  draw_line();
  read_options(argc,&(*argv)); /* sets various global variables */

  draw_line();
  get_lowmap(argv[1]);         

  draw_line(); 
  get_centered_structure_and_radius (argv[2], &struct_max_radius);
  draw_line();
  
  /* calculate sigma of kernel (1D) */
  sigma1d = g_target_res / (2.0*g_width*sqrt(3.0)); 
  /* create Gaussian kernel */ 
  create_gaussian (&g_phi_ga, &g_nvox_ga, &g_ext_ga, sigma1d, 3.0);
 

  
  grid_extent_pdb = ceil(struct_max_radius/g_width)+1;
  if (grid_extent_pdb >  g_extx) zeropad[0] = ceil((grid_extent_pdb-g_extx)/2);
  if (grid_extent_pdb >  g_exty) zeropad[1] = ceil((grid_extent_pdb-g_exty)/2);
  if (grid_extent_pdb >  g_extz) zeropad[2] = ceil((grid_extent_pdb-g_extz)/2);

  for (m=0;m<3;m++)
    zeropad[m]+= (g_ext_ga+1)/2;

  /* now add extra padding to g_phi_lo, changing the map size parameters */  
  create_padded_map (&g_phi_du, &g_extx, &g_exty, &g_extz, &g_gridx, &g_gridy, &g_gridz, &g_nvox, 
		     g_phi_lo, g_extx, g_exty, g_extz, g_gridx, g_gridy, g_gridz, 
		     g_width, g_width, g_width, zeropad); 


  /* allocate memory */
  cp_vect_destroy(&g_phi_lo,&g_phi_du,g_nvox);
 
  draw_line();
  printf("frmv> Projecting probe structure to lattice...\n");
  do_vect(&g_phi_hi,g_nvox); 
  project_mass (&g_phi_hi, g_nvox, g_width, g_width, g_width, g_extx, g_exty, g_extz, g_pdb_original, g_num_atoms, zero_shift);


  printf("frmv> Low-pass-filtering probe map...\n");
  convolve_kernel_inside (&g_phi_hi, g_phi_hi, g_extx, g_exty, g_extz, g_phi_ga, g_ext_ga);
  
  /* compute adequate cutoff for the high map */
  max_dens_hi=*(g_phi_hi+0);
  max_dens_lo=*(g_phi_lo+0);
  for(i=0;i<g_nvox;i++){
    if (*(g_phi_hi+i)>max_dens_hi)
      max_dens_hi=*(g_phi_hi+i);
    if (*(g_phi_lo+i)>max_dens_lo)
      max_dens_lo=*(g_phi_lo+i);
  }
  g_high_cutoff=(max_dens_hi/max_dens_lo)*g_low_cutoff; 

  /* cutoff everything under g_high_cutoff */
  threshold(g_phi_hi, g_nvox, g_high_cutoff);
  printf("frmv> High map cuttoff=%7.3f\n", g_high_cutoff); 


  /* ==================== FRMV PRECOMPUTATIONS =======================*/  
  draw_line();
  fprintf(stderr, "frmv> Precomputations for FST and d-matrices...");
  time00=get_the_time();

  log2s=6;                   /* log2(size) */
  size=ldexp(1,log2s)+0.1;
  bw=size/2; size2=size*size;
  dist_cut=3.0;
  cut_naive=bw;
             
  do_vect(&seminaive_naive_tablespace, Reduced_Naive_TableSize(bw,cut_naive) +
	  Reduced_SpharmonicTableSize(bw,cut_naive));
  do_vect(&workspace,(8*bw*bw+16*bw));
  do_vect(&ddd, bw*(4*bw*bw-1)/3);

  seminaive_naive_table = 
    (double **)SemiNaive_Naive_Pml_Table(bw, cut_naive,
					 seminaive_naive_tablespace,
					 workspace); 
  wigner(bw, 0.5*M_PI, ddd); 


  /* FFTW initialization */
  plan_fftw=fftw3d_create_plan(size, size, size, FFTW_BACKWARD,
                               FFTW_ESTIMATE | FFTW_IN_PLACE);  


  itime = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(itime, time00))));

  time01 = get_the_time();
  fprintf(stderr, "frmv> Computing COM of high-res map...");
  cen_of_mass(g_phi_hi, &comx_hi, &comy_hi, &comz_hi);  /* determine COM of high-res map */
  time02 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time02, time01))));

  fprintf(stderr, "frmv> Computing COM of low-res  map...");
  cen_of_mass(g_phi_lo, &comx_lo, &comy_lo, &comz_lo);  /* determine COM of low-res map */
  time03 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time03, time02))));

 
  /* ==================== MAPS SAMPLING  =======================*/
 
  max_r=ceil(sqrt((double)(g_extx*g_extx+g_exty*g_exty+g_extz*g_extz)))+1;
  do_mat(&sph_sampl_lo,max_r,size*size);
  do_mat(&sph_sampl_hi,max_r,size*size);
 
  /* sample high res. map */
  fprintf(stderr, "frmv> Sampling high resolution  map...");
  volumetric_sampling(g_phi_hi, comx_hi, comy_hi, comz_hi, sph_sampl_hi, bw, &rmax_dens_hi, max_r);   
  time04 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time04, time03))));
  free(g_phi_hi);

  /* sample low res. map */
  fprintf(stderr, "frmv> Sampling low resolution map...");
  time05 = get_the_time();
  volumetric_sampling(g_phi_lo, comx_lo, comy_lo, comz_lo, sph_sampl_lo, bw, &rmax_dens_lo, max_r);    
  time06 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time06, time05))));
  free(g_phi_lo);



  /* ==================== FRMV COMPUTATIONS =======================*/ 

  /* compute coefficients */
  fprintf(stderr, "frmv> Computing coefficients and integrals...");
  time07 = get_the_time();

  /* allocate memory */
  do_vect(&idata,size*size);
  do_vect(&integralr,bw*(4*bw*bw-1)/3);
  do_vect(&integrali,bw*(4*bw*bw-1)/3);
  do_vect(&coeffr_lo,bw*bw);
  do_vect(&coeffi_lo,bw*bw); 
  do_vect(&coeffr_hi,bw*bw);
  do_vect(&coeffi_hi,bw*bw); 

 
  /* set rmaxm to the smaller of the 2 radii */
  if(rmax_dens_lo<rmax_dens_hi)       
    rmaxm=rmax_dens_lo;
  else
    rmaxm=rmax_dens_hi;

  /* add terms corresponding to r to each integral */
  for(r=1;r<=rmaxm;r++){                     
    
    /* get coefficients for high res. map at r */ 
    FST_semi_memo(sph_sampl_hi[r], idata,      
		  coeffr_hi, coeffi_hi,
		  size,
		  seminaive_naive_table,
		  workspace,
		  1,
		  cut_naive);

    /* get coefficients for low res. map at r */ 
    FST_semi_memo(sph_sampl_lo[r], idata,      
		  coeffr_lo, coeffi_lo,
		  size,
		  seminaive_naive_table,
		  workspace,
		  1,
		  cut_naive);

    /* correction factor for m=0 coefficients */
    for(l=0;l<bw;l++){                        
      coeffr_hi[l] *= SQT2;
      coeffr_lo[l] *= SQT2;
    }

    r2=r*r;
    for(l=0, tl=0;l<bw;l++, tl+=2){
      init=l*(tl*tl-1)/3;
      for(i=0;i<=tl;i++){
        ind1=seanindex(i-l,l,bw);     /* i-l=m  */
	index=init+i*(tl+1);
        for(j=0;j<=tl;j++, index++){
          ind2=seanindex(j-l,l,bw);   /* j-l=m' */
          *(integralr+index) += (coeffr_hi[ind2]*coeffr_lo[ind1]+coeffi_hi[ind2]*coeffi_lo[ind1])*r2;
          *(integrali+index) += (coeffr_hi[ind2]*coeffi_lo[ind1]-coeffi_hi[ind2]*coeffr_lo[ind1])*r2;
        }
      }
    }

  }
  time08 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time08, time07))));

  /* free space */
  for(r=0;r<max_r;r++){
    free(sph_sampl_hi[r]);
    free(sph_sampl_lo[r]);
  }
  free(coeffr_hi); free(coeffi_hi);
  free(coeffr_lo); free(coeffi_lo);
  free(workspace); 
  free(seminaive_naive_tablespace);
  free(idata);

  /* Computing Fourier coefficients of the correlation function */
  fprintf(stderr, "frmv> Computing Fourier coefficients of the correlation function...");
  do_vect(&coef_corr,2*size*size2);
  fourier_corr(bw, integralr, integrali, ddd, coef_corr);      /* compute T(p,q,r) */
  time09 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time09, time08))));

  /* free space */
  free(ddd);
  free(integralr); free(integrali);
  
  /* Computing inverse FFT using FFTW */ 
  time09 = get_the_time();
  fprintf(stderr, "frmv> Computing inverse FFT...");
  fftwnd_one(plan_fftw,  (fftw_complex *) coef_corr, NULL);
  fftwnd_destroy_plan(plan_fftw);
  time10 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time10, time09))));


  /*=========================== DETECT AND SORT PEAKS  ============================*/ 

  /* this block searches the relative maxima of the correlation function */
  /* and stores them in the array corr */
  /* j ranges over half the values due to periodicity */
  
  for(i=0;i<4;i++){
    corr[i]  = (double *) malloc(1 *sizeof(double));
    if(corr[i] == NULL){
      perror("Error in allocating memory -1\n");
      exit(1);
    }
  }
  
  npeaks=0;                      
  for(i=0;i<size;i++){           
    ind1=i*size2;
    for(j=0;j<=bw;j++){         
      ind2=ind1+j*size;
      for(k=0;k<size;k++){
	ind3=ind2+k;
        
	if ((f020=coef_corr[2*(ind3+size)])<=(f000=coef_corr[2*ind3])) {       
	  if (i==0) f100=coef_corr[2*(ind3+(size-1)*size2)];
	  else f100=coef_corr[2*(ind3-size2)];
	  if (f100<=f000) {         
	    if (i==size-1) f200=coef_corr[2*(j*size+k)];
	    else f200=coef_corr[2*(ind3+size2)];
	    if (f200<=f000) {         
	      if (j==0) f010=coef_corr[2*(ind3+size2-size)];
	      else f010=coef_corr[2*(ind3-size)];
	      if (f010<=f000) {
		if(k==0) f001=coef_corr[2*(ind3+size-1)];
		else f001=coef_corr[2*(ind3-1)];
		if (f001<=f000) {
		  if(k==size-1) f002=coef_corr[2*ind2];
		  else f002=coef_corr[2*(ind3+1)];
		  if (f002<=f000) {
	 
		    tempi=0.0; tempj=0.0; tempk=0.0;
	  
		    if((temp=f100+f200-2*f000)!=0)
		      tempi=(f100-f200)/(2*temp);         
		    phe=(i+tempi)*M_PI/bw;

		    if((temp=f010+f020-2*f000)!=0)
		      tempj=(f010-f020)/(2*temp);
		    phc=(j+tempj)*M_PI/bw;

		    if((temp=f001+f002-2*f000)!=0)
		      tempk=(f001-f002)/(2*temp);
		    ohm=(k+tempk)*M_PI/bw;
		   
		  
		    /* reallocate memory */   
                   
		    for(l=0;l<4;l++)
		      corr[l]=(double *) realloc(corr[l],(npeaks+1)*sizeof(double));

		    
                    psi=-phe;     psi=psi-2.0*M_PI*floor(psi/2.0/M_PI);
		    th=M_PI-phc; 
		    phi=M_PI-ohm; phi=phi-2.0*M_PI*floor(phi/2.0/M_PI);

		    corr[0][npeaks]=(0.5*(f100+f200)-f000)*tempi*tempi+(0.5*(f010+f020)-f000)*tempj*tempj+
		      (0.5*(f001+f002)-f000)*tempk*tempk+0.5*(f200-f100)*tempi+0.5*(f020-f010)*tempj+
		      0.5*(f002-f001)*tempk+f000;;
		    corr[1][npeaks]=psi;
		    corr[2][npeaks]=th;
		    corr[3][npeaks]=phi;
		    npeaks++;
		  }
		}
	      }
	    }
	  }
	}
      } 
    }
  }
  free(coef_corr);

  /* sort correlation values in decreasing order */
  for(i=0;i<npeaks;i++)      
    for(j=i+1;j<npeaks;j++)
      if(corr[0][i]<corr[0][j])
	for(k=0;k<4;k++)  SWAPPING( corr[k][i], corr[k][j], double );


  /* eliminate close-by solutions */
  for(i=0;i<npeaks;i++)      
    for(j=i+1;j<npeaks;j++)
      if(distance_eulers(i, j, corr)<dist_cut*M_PI/bw) { 
	npeaks--;
	for(k=0;k<4;k++) corr[k][j]=corr[k][npeaks];       
	j--; 
      }
  printf("frmv> %d peaks found\n", npeaks);

  /* sort again correlation values in decreasing order */
  for(i=0;i<npeaks;i++)      
    for(j=i+1;j<npeaks;j++)
      if(corr[0][i]<corr[0][j])
        for(k=0;k<4;k++)  SWAPPING(corr[k][i], corr[k][j],double );

   
  /*=========================== SAVE BEST RESULTS ============================*/ 

  /* show results */
  draw_line(); 
  printf("frmv>        Psi    Theta     Phi      Correlation \nfrmv>\n");

 
  for(i=0; i<npeaks && i<20; i++)         
    printf("frmv> %3d  %6.2f  %6.2f   %6.2f    %9.6f\n", i+1,
           corr[1][i]*180/M_PI, corr[2][i]*180/M_PI, 
	   corr[3][i]*180/M_PI, corr[0][i] );
  draw_line(); 

  fprintf(stderr, "frmv> Saving the best results....");

  /* create the dummy structure g_pdb_move */
  g_pdb_move = (PDB *) malloc(g_num_atoms*sizeof(PDB));

  if (npeaks < g_num_explored) g_num_explored=npeaks;
  for(j=0;j<g_num_explored;j++) {
  
    for(i=1;i<g_num_atoms;i++) g_pdb_move[i]=g_pdb_original[i];

    sprintf(out_string, "frmv_best%ld.pdb",j+1);

    /* shift to COM */
     translate (g_pdb_original, g_pdb_move, g_num_atoms,
	       -(comx_hi-0.5*g_extx)*g_width,
	       -(comy_hi-0.5*g_exty)*g_width,
	       -(comz_hi-0.5*g_extz)*g_width);     
  
    /* rotate pdb wrt its COM=(0,0,0) */
    rot_euler(g_pdb_move, g_pdb_move, g_num_atoms, corr[1][j], corr[2][j], corr[3][j]);
   
    /* translate pdb to its final position */
    translate(g_pdb_move, g_pdb_move, g_num_atoms, comx_lo*g_width+g_gridx,
	      comy_lo*g_width+g_gridy, comz_lo*g_width+g_gridz);

    /* save pdb */
    writepdb(out_string,  g_num_atoms, g_pdb_move);                               
  } 

  time11 = get_the_time();
  printf(" done. Time: %s\n", smart_sprint_time(time_to_sec(time_diff(time11, time10))));

  etime = get_the_time();
  printf("frmv> Total time: %s\n", 
	 smart_sprint_time(time_to_sec(time_diff(etime, itime))));
  draw_line(); 
  free(g_pdb_original); free(g_pdb_move);
  free(corr);
  
  return 0;
}


/*====================================================================*/
static void fourier_corr(int bw, double *coeffr, double *coeffi, double *ddd, double *coef_corr){
  /* computes the Fourier coefficients of the correlation function */
  
  int l, p, q, r, z, zi, zii, size=bw<<1, tsize=size<<1, isigp=-1, isigr, tl=0, tr;
  double temp_r, temp_i, tempd;
  unsigned long index, iindex, indexn, init, ind1, ind3, indexa, indexamod, indexan,
    indexb, indexbn, size2, tsize2, tsize3, indexnmod, indexmod;

  size2=size*size;
  tsize2=2*size2;
  tsize3=tsize2*size;

  for(index=0;index<tsize3;index++)
    *(coef_corr+index)=0.0;

  for(l=0;l<bw;l++, tl+=2){        /* compute T(p,q,r) for p>=0 and q>=0 */
    ind1=(init=l*(tl*tl-1)/3)+(tl+1)*l;
    indexa=indexamod=tsize-tl;
    for(p=0;p<=l;p++, ind1+=tl+1,indexa=indexamod+=tsize2){
      iindex=ind1;
      for(r=0;r<l;r++,indexa+=2, iindex++){
        for(q=l, z=0;q<=tl;q++,z++){
	  tempd = ddd[ind1+ q] * ddd[init+ q*(tl+1)+r];
	  index=indexa+ z * tsize;
	  *(coef_corr + index)     += *(coeffr+iindex) * tempd;
	  *(coef_corr + index + 1) += *(coeffi+iindex) * tempd;
	}
      }
      indexa-=tsize;
      for(r=l;r<=tl;r++, indexa+=2, iindex++){
        for(q=l, z=0 ;q<=tl;q++,z++){
	  tempd = ddd[ind1+q] * ddd[init+ q*(tl+1) + r];
	  index=indexa+ z*tsize;
	  *(coef_corr + index)     += *(coeffr+iindex) * tempd;
	  *(coef_corr + index + 1) += *(coeffi+iindex) * tempd;
	}
      }
    }
  }

  for(p=0, indexa= 0;p<bw;p++, indexa+=size2){   /* fill in the region p>=0,q<0 of T(p,q,r) */
    isigp = -isigp;                     /* parity of p */
    zi=(indexa+bw+size2)<<1;
    zii=zi-tsize2;
    for(q=-bw+1;q<0;q++){
      isigr=1;
      index=indexmod=zi+q*tsize;
      indexn=indexnmod=zii-q*tsize;
      for(tr=2;tr<size;tr+=2){          /* for r=-(bw-1),...,-1  ("tr=-2r") */
	isigr=-isigr;                   /* parity of r */
        index+=2;
	indexn+=2;
        /* this is coef_corr[indexn]*(-1)^(p+r) */
        *(coef_corr + index)     = isigp * isigr * *(coef_corr + indexn);
	*(coef_corr + index + 1) = isigp * isigr * *(coef_corr + indexn + 1);
      }
      index=indexmod-size;
      indexn=indexnmod-size;
      for(r=0;r<bw;r++){
        isigr=-isigr;                   /* parity of r */
	/* this is coef_corr[indexn]*(-1)^(p+r) */
        *(coef_corr + index)     = isigp * isigr * *(coef_corr + indexn);
	*(coef_corr + index + 1) = isigp * isigr * *(coef_corr + indexn + 1);
        index+=2;
	indexn+=2;
      }
    }
  }

  for(p=-bw+1;p<0;p++){                 /* fill in the region p<0 of T(p,q,r) */
    indexa=(p+size)*size2;
    indexan=-p*size2;
    for(q=-bw+1;q<bw;q++){
      indexb=indexa+prime(q, size)*size;
      indexbn=indexan+prime(-q, size)*size;
      for(r=-bw+1;r<bw;r++){
        index=(indexb+prime(r, size))<<1;
	indexn=(indexbn+prime(-r, size))<<1;
        *(coef_corr + index)     =  *(coef_corr + indexn);
	*(coef_corr + index + 1) = -*(coef_corr + indexn + 1);
      }
    }
  }
}
  

/*====================================================================*/

static void volumetric_sampling(double *phi, double cx, double cy, double cz, double *sample[], int bw, int *rmax, int maxext ){
/* performs the sampling in spherical coordinates */

  int i, j, r, size;
  double lambda, theta, initlambda;          /* longitude and latitude */
  double stsl, stcl, st, ct;
  double x, y, z;
  double a, b, c;
  int x1, y1, z1;
  double f111, f112, f121, f122, f211, f212, f221, f222;
  unsigned long index;
  

  size=(bw<<1);
  initlambda=M_PI/bw;
 
    
  for(i=0;i<size;i++){           /* i represents latitude values */
    theta=latitude(i, bw);
    index=i*size;
    st=sin(theta); ct=cos(theta);  
    for(j=0,lambda=0; j<size;j++,index++, lambda+=initlambda){         /* j represents longitude values */
      stsl=st*sin(lambda); stcl=st*cos(lambda);
      for(r=0, x = cx, y=cy, z=cz;r<maxext;r++, x+=stcl, y+=stsl, z+=ct){
	if(x<0.0 || x>=g_extx-1.0 || y<0.0 || y>=g_exty-1.0 || z<0.0 || z>=g_extz-1.0){
          for(;r<maxext;r++)
            *(sample[r]+index)=0.0;
          break;
        } 
  
        /* interpolation */
        x1=floor(x); y1=floor(y); z1=floor(z);
	a=x-x1; b=y-y1; c=z-z1;
	f111=*(phi+gidz_general(z1, y1, x1, g_exty, g_extx));
	f112=*(phi+gidz_general(z1+1, y1, x1,g_exty,g_extx));
	f121=*(phi+gidz_general(z1, y1+1, x1,g_exty,g_extx));
	f122=*(phi+gidz_general(z1+1, y1+1, x1,g_exty,g_extx));
	f211=*(phi+gidz_general(z1, y1, x1+1,g_exty,g_extx));
	f212=*(phi+gidz_general(z1+1, y1, x1+1,g_exty,g_extx));
	f221=*(phi+gidz_general(z1, y1+1, x1+1,g_exty,g_extx));
	f222=*(phi+gidz_general(z1+1, y1+1, x1+1,g_exty,g_extx));
	*(sample[r]+index)=(1-a)*((1-b)*((1-c)*f111+c*f112)+b*((1-c)*f121+c*f122))+
	  a *((1-b)*((1-c)*f211+c*f212)+b*((1-c)*f221+c*f222));
      }
    }
  }
  /* rmax: maximum distance from COM to starred hull of map */
  *rmax=0;                    
  for(i=0;i<size;i++){
    index=i*size;
    for(j=0;j<size;j++,index++)
      for(r=maxext-1;r>=0;r--)
        if(*(sample[r]+index)>0.0){
          if(r> *rmax) *rmax=r;
          break;
        }
  }

}


/*====================================================================*/
static void cen_of_mass(double *phi, double *cx, double *cy, double *cz){
  /* Computes the center of mass of the density phi */

  unsigned long i, j, k, ind;
  double mass;
  double cxap, cyap, czap;

  cxap=0.0; cyap=0.0; czap=0.0; mass=0.0;
  for (k=0;k<g_extz;k++) 
    for (j=0;j<g_exty;j++)
      for (i=0;i<g_extx;i++){
        ind=gidz_general(k, j, i,g_exty,g_extx);
        cxap += *(phi+ind)*i;
        cyap += *(phi+ind)*j;
        czap += *(phi+ind)*k;
	mass += *(phi+ind);
      }

  cxap /= mass; cyap /= mass; czap /= mass;

  *cx=cxap; *cy=cyap; *cz=czap;
}


/*====================================================================*/
static double longitude(int j, int bw){
  return M_PI*j/bw;
}


/*====================================================================*/
static double latitude(int i, int bw){
  return 0.5*M_PI*(i+0.5)/bw;
}


/*====================================================================*/
static void wigner(int bw, double theta, double *ddd){
  /* computes the d-functions for argument theta, for degrees 0 through bw-1 */
  /* the matrices are returned in the (3D) piramid ddd */
  /* Reference: T. Risbo, Journal of Geodesy (1996) 70:383-396 */

  double p, q, pc, qc, temp, *d, *dd;
  int size, index, i, j2, k, l, hdeg;
  unsigned long init;
  double fact1, fact2, fact3, fact4;

  size=2*bw;
  
  d  = (double *) malloc(size*size*sizeof(double));
  dd = (double *) malloc(size*size*sizeof(double));

  if( (d == NULL) || (dd == NULL) ){
    perror("Error in allocating memory");
    exit(1);
  }

  p=sin(theta/2); q=cos(theta/2);   /* Cayley-Klein parameters */
  pc=p; qc=q;

  *(ddd+0)=1.0;                     /* d-matrix of degree 0 */
  
  /* d-matrix of degree 1/2 */
  *(d+0)=q;
  *(d+1)=p;
  *(d+1*size+0)=-pc;
  *(d+1*size+1)=qc;
  
  for(l=1;l<bw;l++){       /* l is the degree of the next d-matrix to be saved in ddd */
    j2=(l<<1)-1;           /* j2 will be twice the degree of the d-matrix about to be computed */
    for(hdeg=0;hdeg<2;hdeg++){
      fact1=q/ ++j2;
      fact2=pc/j2;
      fact3=p/j2;
      fact4=qc/j2;
      for(i=0;i<=j2+1;i++)
        for(k=0;k<=j2+1;k++)
          *(dd+i*size+k)=0.0;
      for(i=0;i<j2;i++)
        for(k=0;k<j2;k++){
          index=i*size+k;
          temp=*(d+index);
          *(dd+index)        += sqrt((j2-i)*(j2-k))*temp*fact1;
	  *(dd+index+size)   += -sqrt((i+1)*(j2-k))*temp*fact2;
	  *(dd+index+1)      += sqrt((j2-i)*(k+1)) *temp*fact3;
	  *(dd+index+size+1) += sqrt((i+1) *(k+1)) *temp*fact4;
        }
      for(i=0;i<=j2;i++)        /* move dd to d */
        for(k=0;k<=j2;k++)
          *(d+i*size+k)=*(dd+i*size+k);
      if(hdeg==0){              /* if degree is integer, copy d to the proper location in ddd */
        init=l*(4*l*l-1)/3;
        for(i=0;i<=j2;i++)
          for(k=0;k<=j2;k++)
            *(ddd+init+i*(j2+1)+k) = *(d+i*size+k);
      }
      if(l==bw-1) break;     /* for l=bw-1 do hdeg=0 only */
    }
  }
  free(d); free(dd);
}



/*====================================================================*/
static int prime(int n, int s){
  /* returns n if it is >=0, or n+s otherwise */

  if(n>=0) return n;
  return n+s;
}


/*====================================================================*/
static double distance_eulers(unsigned long i, unsigned long j, double *corr[]){
  /* returns the distance between the rotations given by the Euler angles in
     corr[1,2,3][i] and corr[1,2,3][j] */

  double matrix1[3][3],matrix2[3][3]; 
  int k, l;
  double temp, trace;
  
  get_rot_matrix(matrix1,corr[1][i],corr[2][i],corr[3][i]);
  get_rot_matrix(matrix2,corr[1][j],corr[2][j],corr[3][j]);
  

  trace=0.0;             /* trace(matrix1*transpose(matrix2)) */
  for(k=0;k<3;k++)
    for(l=0;l<3;l++)
      trace += matrix1[k][l]*matrix2[k][l];

  temp=0.5*(trace-1.0);
  if(temp>=1.0)
    return 0.0;
  if(temp<=-1.0)
    return M_PI;
  return acos(temp);
}


/*====================================================================*/
static void read_options(int argc, char **argv) {
  /* print usage info and read options from input arguments */
  
  char *pos;
  int i;
  char option_string[199];
  
  if(argc<2) { /* print usage and options info */

    printf("frmv> USAGE:  frmv <Situs density map> <PDB structure> <options>\n"); 
    printf("frmv>\n");
    printf("frmv> OPTIONS:\n"); 
    printf("frmv>\n");
    printf("frmv>\t-res <float>\t   Target resolution in A [default: -res 15]\n"); 
    printf("frmv>\t-cutoff <float>\t   Density map cutoff value [default: -cutoff 0.0]\n");
    printf("frmv>\t-explor <int>\t   Number of local maxima explored [default: -explor 5]\n");
    printf("frmv>\n");
    draw_line();
    exit(0);
  }
 
  /* now read options from arguments and assign global variables */
  
  sprintf(option_string,"");
  printf("frmv> Options read:\n");
  for(i=1;i<argc;i++) sprintf(option_string,"%s %s",option_string,argv[i]);
  
  /* target resolution */
  g_target_res=15.0;
  if((pos=(char *)strstr(option_string," -res"))!=NULL)  
    sscanf(pos+5,"%lf",&g_target_res);
  printf("frmv> Target resolution %3.3f\n",g_target_res);
  
  /* cutoff of the low-resolution map */
  g_low_cutoff=0;
  if((pos=(char *)strstr(option_string," -cutoff"))!=NULL)  
    sscanf(pos+8,"%lf",&g_low_cutoff);
  printf("frmv> Low-resolution map cutoff %3.3f\n",g_low_cutoff);
 
  /* number of best fits */
  g_num_explored=5;
  if((pos=(char *)strstr(option_string," -explor"))!=NULL)
    sscanf(pos+8,"%d",&g_num_explored);
  printf("frmv> Number of best fits explored %2d\n",g_num_explored);
}

 
/*====================================================================*/
static void get_lowmap(char *file_name) {
  /* reads low resolution map from file_name */

  printf("frmv> Processing low-resolution map.\n");

  readvol(file_name, &g_width, &g_gridx, &g_gridy, &g_gridz, &g_extx, &g_exty, &g_extz, &g_phi_lo);
  g_nvox = g_extx*g_exty*g_extz;

  /* set density values below g_low_cutoff to zero */
  threshold(g_phi_lo, g_nvox, g_low_cutoff);

  /* shrink map about non-zero density and resize to odd intervals */
  shrink_margin(&g_phi_du, &g_extx, &g_exty, &g_extz, &g_gridx, &g_gridy, &g_gridz, &g_nvox, 
		g_phi_lo, g_extx, g_exty, g_extz, g_gridx, g_gridy, g_gridz, g_width);
  cp_vect_destroy(&g_phi_lo,&g_phi_du,g_nvox); 

  print_map_info(g_phi_lo, g_nvox);
}


/*====================================================================*/
static void get_centered_structure_and_radius (char *file_name, double *max_radius) {
  /* reads atomic structure and centers it */

  double com_x; 
  double com_y;
  double com_z;

  printf("frmv> Processing atomic structure.\n");  

  /* read PDB file */
  read_and_weight_mass (file_name, &g_num_atoms, &g_pdb_original);
   
  calc_center_mass (g_pdb_original, g_num_atoms, &com_x, &com_y, &com_z);
  *max_radius = calc_sphere(g_pdb_original,g_num_atoms,com_x,com_y,com_z);
  printf ("frmv> COM: %6.3f %6.3f %6.3f, radius: %6.3f Angstrom\n",com_x,com_y,com_z,*max_radius);
  
  /* center structure */ 
  translate (g_pdb_original, g_pdb_original, g_num_atoms, -com_x, -com_y, -com_z);
}


/*====================================================================*/
static void draw_line() {
  printf("_______________________________________________________________________________________\n\n");
}
