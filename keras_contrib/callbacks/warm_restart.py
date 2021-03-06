import numpy as np
from keras.callbacks import Callback
import keras.backend as K


class LearningRateWarmRestarter(Callback):
    """Warm Restart Learning rate update rule.
    Warm restart technique is a way to improve the rate of convergence for stochastic gradient descent.

    # Arguments
        min_lr: lower bound on the learning rate.
        max_lr: upper bound on the learning rate.
        num_restart_epochs:  restart learning rate from `max_lr` at every `num_restart_epochs`.
        factor: a factor by which the number of restart epochs will be increased. `new_num_restart_epochs = num_restart_epochs * factor`.

    # Reference
        [SGDR: Stochastic Gradient Descent with Warm Restarts](https://arxiv.org/pdf/1608.03983.pdf)

    # Example

    ```python
    warm_restart_lr = LearningRateWarmRestarter(min_lr=0., max_lr=0.1,
                                                num_restart_epochs=5, factor=2)
    model.fit(x_train, y_train, callbacks=[warm_restart_lr])
    ```
    """

    def __init__(self, min_lr=0., max_lr=0.1, num_restart_epochs=5, factor=2):
        super(LearningRateWarmRestarter, self).__init__()
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.num_restart_epochs = num_restart_epochs
        self.factor = factor
        self.next_restart_epochs = 0

        if factor < 1:
            raise ValueError('"factor" must be larger than 1 or equal 1')

    def on_epoch_begin(self, epoch, logs=None):
        if not hasattr(self.model.optimizer, 'lr'):
            raise ValueError('Optimizer must have a "lr" attribute.')

        t = epoch - self.next_restart_epochs

        # check whether restart or not
        if t == self.num_restart_epochs:
            self.next_restart_epochs += self.num_restart_epochs
            self.num_restart_epochs *= self.factor
            t = 0

        new_lr = self.min_lr + 0.5 * (self.max_lr - self.min_lr) * (1. + np.cos(t / self.num_restart_epochs * np.pi))
        K.set_value(self.model.optimizer.lr, new_lr)
