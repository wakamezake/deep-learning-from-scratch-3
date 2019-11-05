import numpy as np
import contextlib


class Config:
    enable_backprop = True


config = Config()


@contextlib.contextmanager
def using_config(name, value):
    old_value = getattr(config, name)
    setattr(config, name, value)
    try:
        yield
    finally:
        setattr(config, name, old_value)


def no_grad():
    return using_config('enable_backprop', False)


class Variable:

    def __init__(self, data, name=None):
        self.data = data
        self.name = name
        self.grad = None
        self.creator = None
        self.priority = 0

    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return self.data.ndim

    @property
    def size(self):
        return self.data.size

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def array(self):
        return self.data

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        name = '' if self.name is None else ' ' + self.name
        return '%s%s(%s)' % ('variable', name, np.array2string(self.data))

    def set_creator(self, func):
        self.creator = func
        self.priority = func.priority + 1

    def cleargrad(self):
        self.grad = None

    def backward(self, retain_grad=False):
        if self.grad is None:
            self.grad = np.ones_like(self.data)

        funcs = []
        seen_set = set()

        def add_func(f):
            if f not in seen_set:
                funcs.append(f)
                seen_set.add(f)
                funcs.sort(key=lambda x: x.priority)

        add_func(self.creator)

        while funcs:
            f = funcs.pop()
            gys = [output.grad for output in f.outputs]
            gxs = f.backward(*gys)
            if not isinstance(gxs, tuple):
                gxs = (gxs,)

            for x, gx in zip(f.inputs, gxs):
                if x.grad is None:
                    x.grad = gx
                else:
                    x.grad = x.grad + gx

                if x.creator is not None:
                    add_func(x.creator)

            if not retain_grad:
                for y in f.outputs:
                    y.cleargrad()


class Function:

    def __call__(self, *inputs):
        xs = [x.data for x in inputs]
        ys = self.forward(*xs)
        if not isinstance(ys, tuple):
            ys = (ys,)
        outputs = [Variable(y) for y in ys]

        if config.enable_backprop:
            self.priority = max([x.priority for x in inputs])
            for output in outputs:
                output.set_creator(self)
            self.inputs = inputs
            self.outputs = outputs

        return outputs if len(outputs) > 1 else outputs[0]

    def forward(self, xs):
        raise NotImplementedError()

    def backward(self, gys):
        raise NotImplementedError()


class Square(Function):

    def forward(self, x):
        return x ** 2

    def backward(self, gy):
        x = self.inputs[0].data
        return 2 * x * gy


def square(x):
    f = Square()
    return f(x)


class Add(Function):

    def forward(self, x0, x1):
        y = x0 + x1
        return y

    def backward(self, gy):
        return gy, gy


def add(x0, x1):
    f = Add()
    y = f(x0, x1)
    return y


x = Variable(np.array([[1, 2, 3], [4, 5, 6]]))
print(x.shape)  # (2, 3)

x = Variable(np.array(2.0), 'x')
t = square(x)
y = add(square(t), square(t))
y.name = 'y'
print(x)  # variable x(2.)
print(t)  # variable(4.)
print(y)  # variable y(32.)