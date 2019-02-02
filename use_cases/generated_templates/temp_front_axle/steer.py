
import numpy as np
import scipy as sc
from numpy.linalg import multi_dot
from source.cython_definitions.matrix_funcs import A, B, triad as Triad
from scipy.misc import derivative
from numpy import cos, sin
import pandas as pd

def Mirror(v):
    if v.shape in ((1,3),(4,1)):
        return v
    else:
        m = np.array([[1,0,0],[0,-1,0],[0,0,1]],dtype=np.float64)
        return m.dot(v)


class configuration(object):

    def __init__(self):
        self.R_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_rbs_coupler = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rd_rbs_coupler = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_rbs_coupler = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.R_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.P_rbr_rocker = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.Rd_rbr_rocker = np.array([[0], [0], [0]],dtype=np.float64)
        self.Pd_rbr_rocker = np.array([[0], [0], [0], [0]],dtype=np.float64)
        self.ax1_jcs_rc_sph = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcs_rc_sph = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax1_jcs_rc_cyl = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcs_rc_cyl = np.array([[0], [0], [0]],dtype=np.float64)
        self.ax1_jcr_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)
        self.pt1_jcr_rocker_ch = np.array([[0], [0], [0]],dtype=np.float64)

        self._set_arguments()

    def _set_arguments(self):
        self.R_rbl_rocker = Mirror(self.R_rbr_rocker)
        self.P_rbl_rocker = Mirror(self.P_rbr_rocker)
        self.Rd_rbl_rocker = Mirror(self.Rd_rbr_rocker)
        self.Pd_rbl_rocker = Mirror(self.Pd_rbr_rocker)
        self.ax1_jcl_rocker_ch = Mirror(self.ax1_jcr_rocker_ch)
        self.pt1_jcl_rocker_ch = Mirror(self.pt1_jcr_rocker_ch)

    def load_from_csv(self,csv_file):
        dataframe = pd.read_csv(csv_file,index_col=0)
        for ind in dataframe.index:
            shape = getattr(self,ind).shape
            v = np.array(dataframe.loc[ind],dtype=np.float64)
            v = np.resize(v,shape)
            setattr(self,ind,v)
        self._set_arguments()

    def eval_constants(self):

        c0 = A(self.P_rbs_coupler).T
        c1 = Triad(self.ax1_jcs_rc_sph,)
        c2 = A(self.P_rbr_rocker).T
        c3 = self.pt1_jcs_rc_sph
        c4 = -1.0*multi_dot([c0,self.R_rbs_coupler])
        c5 = -1.0*multi_dot([c2,self.R_rbr_rocker])
        c6 = Triad(self.ax1_jcs_rc_cyl,)
        c7 = A(self.P_rbl_rocker).T
        c8 = self.pt1_jcs_rc_cyl
        c9 = -1.0*multi_dot([c7,self.R_rbl_rocker])
        c10 = Triad(self.ax1_jcr_rocker_ch,)
        c11 = A(self.P_vbs_chassis).T
        c12 = self.pt1_jcr_rocker_ch
        c13 = -1.0*multi_dot([c11,self.R_vbs_chassis])
        c14 = Triad(self.ax1_jcl_rocker_ch,)
        c15 = self.pt1_jcl_rocker_ch

        self.Mbar_rbs_coupler_jcs_rc_sph = multi_dot([c0,c1])
        self.Mbar_rbr_rocker_jcs_rc_sph = multi_dot([c2,c1])
        self.ubar_rbs_coupler_jcs_rc_sph = (multi_dot([c0,c3]) + c4)
        self.ubar_rbr_rocker_jcs_rc_sph = (multi_dot([c2,c3]) + c5)
        self.Mbar_rbs_coupler_jcs_rc_cyl = multi_dot([c0,c6])
        self.Mbar_rbl_rocker_jcs_rc_cyl = multi_dot([c7,c6])
        self.ubar_rbs_coupler_jcs_rc_cyl = (multi_dot([c0,c8]) + c4)
        self.ubar_rbl_rocker_jcs_rc_cyl = (multi_dot([c7,c8]) + c9)
        self.Mbar_rbr_rocker_jcr_rocker_ch = multi_dot([c2,c10])
        self.Mbar_vbs_chassis_jcr_rocker_ch = multi_dot([c11,c10])
        self.ubar_rbr_rocker_jcr_rocker_ch = (multi_dot([c2,c12]) + c5)
        self.ubar_vbs_chassis_jcr_rocker_ch = (multi_dot([c11,c12]) + c13)
        self.Mbar_rbl_rocker_jcl_rocker_ch = multi_dot([c7,c14])
        self.Mbar_vbs_chassis_jcl_rocker_ch = multi_dot([c11,c14])
        self.ubar_rbl_rocker_jcl_rocker_ch = (multi_dot([c7,c15]) + c9)
        self.ubar_vbs_chassis_jcl_rocker_ch = (multi_dot([c11,c15]) + c13)

    @property
    def q(self):
        q = np.concatenate([self.R_rbs_coupler,self.P_rbs_coupler,self.R_rbr_rocker,self.P_rbr_rocker,self.R_rbl_rocker,self.P_rbl_rocker])
        return q

    @property
    def qd(self):
        qd = np.concatenate([self.Rd_rbs_coupler,self.Pd_rbs_coupler,self.Rd_rbr_rocker,self.Pd_rbr_rocker,self.Rd_rbl_rocker,self.Pd_rbl_rocker])
        return qd



class topology(object):

    def __init__(self,config,prefix=''):
        self.t = 0.0
        self.config = config
        self.prefix = (prefix if prefix=='' else prefix+'.')

        self.n = 21
        self.nrows = 14
        self.ncols = 2*5
        self.rows = np.arange(self.nrows)

        self.jac_rows = np.array([0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,12,13])                        

    
    def _set_mapping(self,indicies_map,interface_map):
        p = self.prefix
        self.rbs_coupler = indicies_map[p+'rbs_coupler']
        self.rbr_rocker = indicies_map[p+'rbr_rocker']
        self.rbl_rocker = indicies_map[p+'rbl_rocker']
        self.vbs_chassis = indicies_map[interface_map[p+'vbs_chassis']]
        self.vbs_ground = indicies_map[interface_map[p+'vbs_ground']]

    def assemble_template(self,indicies_map,interface_map,rows_offset):
        self.rows_offset = rows_offset
        self._set_mapping(indicies_map,interface_map)
        self.rows += self.rows_offset
        self.jac_rows += self.rows_offset
        self.jac_cols = np.array([self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbs_coupler*2,self.rbs_coupler*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbr_rocker*2,self.rbr_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbl_rocker*2,self.rbl_rocker*2+1,self.vbs_chassis*2,self.vbs_chassis*2+1,self.rbs_coupler*2+1,self.rbr_rocker*2+1,self.rbl_rocker*2+1])

    def set_initial_states(self):
        self.set_gen_coordinates(self.config.q)
        self.set_gen_velocities(self.config.qd)

    
    def set_gen_coordinates(self,q):
        self.R_rbs_coupler = q[0:3,0:1]
        self.P_rbs_coupler = q[3:7,0:1]
        self.R_rbr_rocker = q[7:10,0:1]
        self.P_rbr_rocker = q[10:14,0:1]
        self.R_rbl_rocker = q[14:17,0:1]
        self.P_rbl_rocker = q[17:21,0:1]

    
    def set_gen_velocities(self,qd):
        self.Rd_rbs_coupler = qd[0:3,0:1]
        self.Pd_rbs_coupler = qd[3:7,0:1]
        self.Rd_rbr_rocker = qd[7:10,0:1]
        self.Pd_rbr_rocker = qd[10:14,0:1]
        self.Rd_rbl_rocker = qd[14:17,0:1]
        self.Pd_rbl_rocker = qd[17:21,0:1]

    
    def eval_pos_eq(self):
        config = self.config
        t = self.t

        x0 = self.R_rbs_coupler
        x1 = self.R_rbr_rocker
        x2 = self.P_rbs_coupler
        x3 = A(x2)
        x4 = self.P_rbr_rocker
        x5 = A(x4)
        x6 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,0:1].T
        x7 = x3.T
        x8 = self.P_rbl_rocker
        x9 = A(x8)
        x10 = config.Mbar_rbl_rocker_jcs_rc_cyl[:,2:3]
        x11 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,1:2].T
        x12 = self.R_rbl_rocker
        x13 = (x0 + -1.0*x12 + multi_dot([x3,config.ubar_rbs_coupler_jcs_rc_cyl]) + -1.0*multi_dot([x9,config.ubar_rbl_rocker_jcs_rc_cyl]))
        x14 = -1.0*self.R_vbs_chassis
        x15 = A(self.P_vbs_chassis)
        x16 = x5.T
        x17 = config.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        x18 = x9.T
        x19 = config.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        x20 = -1.0*np.eye(1,dtype=np.float64)

        self.pos_eq_blocks = [(x0 + -1.0*x1 + multi_dot([x3,config.ubar_rbs_coupler_jcs_rc_sph]) + -1.0*multi_dot([x5,config.ubar_rbr_rocker_jcs_rc_sph])),multi_dot([x6,x7,x9,x10]),multi_dot([x11,x7,x9,x10]),multi_dot([x6,x7,x13]),multi_dot([x11,x7,x13]),(x1 + x14 + multi_dot([x5,config.ubar_rbr_rocker_jcr_rocker_ch]) + -1.0*multi_dot([x15,config.ubar_vbs_chassis_jcr_rocker_ch])),multi_dot([config.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1].T,x16,x15,x17]),multi_dot([config.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2].T,x16,x15,x17]),(x12 + x14 + multi_dot([x9,config.ubar_rbl_rocker_jcl_rocker_ch]) + -1.0*multi_dot([x15,config.ubar_vbs_chassis_jcl_rocker_ch])),multi_dot([config.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1].T,x18,x15,x19]),multi_dot([config.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2].T,x18,x15,x19]),(x20 + (multi_dot([x2.T,x2]))**(1.0/2.0)),(x20 + (multi_dot([x4.T,x4]))**(1.0/2.0)),(x20 + (multi_dot([x8.T,x8]))**(1.0/2.0))]

    
    def eval_vel_eq(self):
        config = self.config
        t = self.t

        v0 = np.zeros((3,1),dtype=np.float64)
        v1 = np.zeros((1,1),dtype=np.float64)

        self.vel_eq_blocks = [v0,v1,v1,v1,v1,v0,v1,v1,v0,v1,v1,v1,v1,v1]

    
    def eval_acc_eq(self):
        config = self.config
        t = self.t

        a0 = self.Pd_rbs_coupler
        a1 = self.Pd_rbr_rocker
        a2 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,0:1]
        a3 = a2.T
        a4 = self.P_rbs_coupler
        a5 = A(a4).T
        a6 = self.Pd_rbl_rocker
        a7 = config.Mbar_rbl_rocker_jcs_rc_cyl[:,2:3]
        a8 = B(a6,a7)
        a9 = a7.T
        a10 = self.P_rbl_rocker
        a11 = A(a10).T
        a12 = B(a0,a2)
        a13 = a0.T
        a14 = B(a4,a2).T
        a15 = B(a10,a7)
        a16 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,1:2]
        a17 = a16.T
        a18 = B(a0,a16)
        a19 = B(a4,a16).T
        a20 = config.ubar_rbs_coupler_jcs_rc_cyl
        a21 = config.ubar_rbl_rocker_jcs_rc_cyl
        a22 = (multi_dot([B(a0,a20),a0]) + -1.0*multi_dot([B(a6,a21),a6]))
        a23 = (self.Rd_rbs_coupler + -1.0*self.Rd_rbl_rocker + multi_dot([B(a10,a21),a6]) + multi_dot([B(a4,a20),a0]))
        a24 = (self.R_rbs_coupler.T + -1.0*self.R_rbl_rocker.T + multi_dot([a20.T,a5]) + -1.0*multi_dot([a21.T,a11]))
        a25 = self.Pd_vbs_chassis
        a26 = config.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        a27 = a26.T
        a28 = self.P_vbs_chassis
        a29 = A(a28).T
        a30 = config.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1]
        a31 = self.P_rbr_rocker
        a32 = A(a31).T
        a33 = B(a25,a26)
        a34 = a1.T
        a35 = B(a28,a26)
        a36 = config.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2]
        a37 = config.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1]
        a38 = config.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        a39 = B(a25,a38)
        a40 = a38.T
        a41 = a6.T
        a42 = B(a28,a38)
        a43 = config.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2]

        self.acc_eq_blocks = [(multi_dot([B(a0,config.ubar_rbs_coupler_jcs_rc_sph),a0]) + -1.0*multi_dot([B(a1,config.ubar_rbr_rocker_jcs_rc_sph),a1])),(multi_dot([a3,a5,a8,a6]) + multi_dot([a9,a11,a12,a0]) + 2.0*multi_dot([a13,a14,a15,a6])),(multi_dot([a17,a5,a8,a6]) + multi_dot([a9,a11,a18,a0]) + 2.0*multi_dot([a13,a19,a15,a6])),(multi_dot([a3,a5,a22]) + 2.0*multi_dot([a13,a14,a23]) + multi_dot([a24,a12,a0])),(multi_dot([a17,a5,a22]) + 2.0*multi_dot([a13,a19,a23]) + multi_dot([a24,a18,a0])),(multi_dot([B(a1,config.ubar_rbr_rocker_jcr_rocker_ch),a1]) + -1.0*multi_dot([B(a25,config.ubar_vbs_chassis_jcr_rocker_ch),a25])),(multi_dot([a27,a29,B(a1,a30),a1]) + multi_dot([a30.T,a32,a33,a25]) + 2.0*multi_dot([a34,B(a31,a30).T,a35,a25])),(multi_dot([a27,a29,B(a1,a36),a1]) + multi_dot([a36.T,a32,a33,a25]) + 2.0*multi_dot([a34,B(a31,a36).T,a35,a25])),(multi_dot([B(a6,config.ubar_rbl_rocker_jcl_rocker_ch),a6]) + -1.0*multi_dot([B(a25,config.ubar_vbs_chassis_jcl_rocker_ch),a25])),(multi_dot([a37.T,a11,a39,a25]) + multi_dot([a40,a29,B(a6,a37),a6]) + 2.0*multi_dot([a41,B(a10,a37).T,a42,a25])),(multi_dot([a43.T,a11,a39,a25]) + multi_dot([a40,a29,B(a6,a43),a6]) + 2.0*multi_dot([a41,B(a10,a43).T,a42,a25])),2.0*(multi_dot([a13,a0]))**(1.0/2.0),2.0*(multi_dot([a34,a1]))**(1.0/2.0),2.0*(multi_dot([a41,a6]))**(1.0/2.0)]

    
    def eval_jac_eq(self):
        config = self.config
        t = self.t

        j0 = np.eye(3,dtype=np.float64)
        j1 = self.P_rbs_coupler
        j2 = -1.0*j0
        j3 = self.P_rbr_rocker
        j4 = np.zeros((1,3),dtype=np.float64)
        j5 = config.Mbar_rbl_rocker_jcs_rc_cyl[:,2:3]
        j6 = j5.T
        j7 = self.P_rbl_rocker
        j8 = A(j7).T
        j9 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,0:1]
        j10 = B(j1,j9)
        j11 = config.Mbar_rbs_coupler_jcs_rc_cyl[:,1:2]
        j12 = B(j1,j11)
        j13 = j9.T
        j14 = A(j1).T
        j15 = multi_dot([j13,j14])
        j16 = config.ubar_rbs_coupler_jcs_rc_cyl
        j17 = B(j1,j16)
        j18 = config.ubar_rbl_rocker_jcs_rc_cyl
        j19 = (self.R_rbs_coupler.T + -1.0*self.R_rbl_rocker.T + multi_dot([j16.T,j14]) + -1.0*multi_dot([j18.T,j8]))
        j20 = j11.T
        j21 = multi_dot([j20,j14])
        j22 = B(j7,j5)
        j23 = B(j7,j18)
        j24 = config.Mbar_vbs_chassis_jcr_rocker_ch[:,2:3]
        j25 = j24.T
        j26 = self.P_vbs_chassis
        j27 = A(j26).T
        j28 = config.Mbar_rbr_rocker_jcr_rocker_ch[:,0:1]
        j29 = config.Mbar_rbr_rocker_jcr_rocker_ch[:,1:2]
        j30 = A(j3).T
        j31 = B(j26,j24)
        j32 = config.Mbar_vbs_chassis_jcl_rocker_ch[:,2:3]
        j33 = j32.T
        j34 = config.Mbar_rbl_rocker_jcl_rocker_ch[:,0:1]
        j35 = config.Mbar_rbl_rocker_jcl_rocker_ch[:,1:2]
        j36 = B(j26,j32)

        self.jac_eq_blocks = [j0,B(j1,config.ubar_rbs_coupler_jcs_rc_sph),j2,-1.0*B(j3,config.ubar_rbr_rocker_jcs_rc_sph),j4,multi_dot([j6,j8,j10]),j4,multi_dot([j13,j14,j22]),j4,multi_dot([j6,j8,j12]),j4,multi_dot([j20,j14,j22]),j15,(multi_dot([j13,j14,j17]) + multi_dot([j19,j10])),-1.0*j15,-1.0*multi_dot([j13,j14,j23]),j21,(multi_dot([j20,j14,j17]) + multi_dot([j19,j12])),-1.0*j21,-1.0*multi_dot([j20,j14,j23]),j0,B(j3,config.ubar_rbr_rocker_jcr_rocker_ch),j2,-1.0*B(j26,config.ubar_vbs_chassis_jcr_rocker_ch),j4,multi_dot([j25,j27,B(j3,j28)]),j4,multi_dot([j28.T,j30,j31]),j4,multi_dot([j25,j27,B(j3,j29)]),j4,multi_dot([j29.T,j30,j31]),j0,B(j7,config.ubar_rbl_rocker_jcl_rocker_ch),j2,-1.0*B(j26,config.ubar_vbs_chassis_jcl_rocker_ch),j4,multi_dot([j33,j27,B(j7,j34)]),j4,multi_dot([j34.T,j8,j36]),j4,multi_dot([j33,j27,B(j7,j35)]),j4,multi_dot([j35.T,j8,j36]),2.0*j1.T,2.0*j3.T,2.0*j7.T]
  
