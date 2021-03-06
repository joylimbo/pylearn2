"""
.. todo::

    WRITEME
"""
import numpy as np
N = np
from pylearn2.datasets import dense_design_matrix
from pylearn2.utils import serial


class CIFAR100(dense_design_matrix.DenseDesignMatrix):
    """
    .. todo::

        WRITEME
    """
    def __init__(self, which_set, center = False,
            gcn = None, toronto_prepro = False,
            axes = ('b', 0, 1, 'c'),
            start = None, stop = None, one_hot = False):
        """
        .. todo::

            WRITEME
        """

        assert which_set in ['train','test']

        path = "${PYLEARN2_DATA_PATH}/cifar100/cifar-100-python/"+which_set

        obj = serial.load(path)
        X = obj['data']

        assert X.max() == 255.
        assert X.min() == 0.

        X = np.cast['float32'](X)
        y = np.asarray(obj['fine_labels'])

        self.center = center

        self.one_hot = one_hot
        if one_hot:
            one_hot = np.zeros((y.shape[0],100),dtype='float32')
            for i in xrange(y.shape[0]):
                one_hot[i,y[i]] = 1.
            y = one_hot

        if center:
            X -= 127.5

        if toronto_prepro:
            assert not center
            assert not gcn
            if which_set == 'test':
                raise NotImplementedError("Need to subtract the mean of the *training* set.")
            X = X / 255.
            X = X - X.mean(axis=0)
        self.toronto_prepro = toronto_prepro

        self.gcn = gcn
        if gcn is not None:
            assert isinstance(gcn,float)
            X = (X.T - X.mean(axis=1)).T
            X = (X.T / np.sqrt(np.square(X).sum(axis=1))).T
            X *= gcn

        if start is not None:
            # This needs to come after the prepro so that it doesn't change the pixel
            # means computed above
            assert start >= 0
            assert stop > start
            assert stop <= X.shape[0]
            X = X[start:stop, :]
            y = y[start:stop]
            assert X.shape[0] == y.shape[0]

        self.axes = axes
        view_converter = dense_design_matrix.DefaultViewConverter((32,32,3), axes)

        super(CIFAR100,self).__init__(X = X, y =y, view_converter = view_converter)

        assert not N.any(N.isnan(self.X))

        # need to support start, stop
        # self.y_fine = N.asarray(obj['fine_labels'])
        # self.y_coarse = N.asarray(obj['coarse_labels'])



    def adjust_for_viewer(self, X):
        """
        .. todo::

            WRITEME
        """
        #assumes no preprocessing. need to make preprocessors mark the new ranges
        rval = X.copy()

        #patch old pkl files
        if not hasattr(self,'center'):
            self.center = False
        if not hasattr(self,'rescale'):
            self.rescale = False
        if not hasattr(self,'gcn'):
            self.gcn = False

        if self.gcn is not None:
            rval = X.copy()
            for i in xrange(rval.shape[0]):
                rval[i,:] /= np.abs(rval[i,:]).max()
            return rval

        if not self.center:
            rval -= 127.5

        if not self.rescale:
            rval /= 127.5

        rval = np.clip(rval,-1.,1.)

        return rval

    def adjust_to_be_viewed_with(self, X, orig, per_example = False):
        """
        .. todo::

            WRITEME
        """
        # if the scale is set based on the data, display X oring the scale determined
        # by orig
        # assumes no preprocessing. need to make preprocessors mark the new ranges
        rval = X.copy()

        #patch old pkl files
        if not hasattr(self,'center'):
            self.center = False
        if not hasattr(self,'rescale'):
            self.rescale = False
        if not hasattr(self,'gcn'):
            self.gcn = False

        if self.gcn is not None:
            rval = X.copy()
            if per_example:
                for i in xrange(rval.shape[0]):
                    rval[i,:] /= np.abs(orig[i,:]).max()
            else:
                rval /= np.abs(orig).max()
            rval = np.clip(rval, -1., 1.)
            return rval

        if not self.center:
            rval -= 127.5

        if not self.rescale:
            rval /= 127.5

        rval = np.clip(rval,-1.,1.)

        return rval

    def get_test_set(self):
        """
        .. todo::

            WRITEME
        """
        return CIFAR100(which_set='test', center=self.center, rescale=self.rescale, gcn=self.gcn,
                one_hot=self.one_hot, toronto_prepro=self.toronto_prepro, axes=self.axes)

