# vim:ts=4:sw=4:expandtab
'''An outgoing pipeline that can handle
strings or files.
'''
try:
    import cStringIO
except ImportError:
    raise ImportError, "cStringIO is required"

_obj_SIO = cStringIO.StringIO
_type_SIO = cStringIO.OutputType
def make_SIO(d):
    t = _obj_SIO()
    t.write(d)
    t.seek(0)
    return t

def get_file_length(f):
    m = f.tell()
    f.seek(0, 2)
    r = f.tell()
    f.seek(m)
    return r

class PipelineCloseRequest(Exception): pass
class PipelineClosed(Exception): pass
    
class Pipeline(object):
    '''A pipeline that supports appending strings or
    files and can read() transparently across object
    boundaries in the outgoing buffer.
    '''
    def __init__(self):
        self.line = []
        self.want_close = False

    def add(self, d):
        '''Add object `d` to the pipeline.
        '''
        if self.want_close:
            raise PipelineClosed

        if type(d) is str:
            if self.line and type(self.line[-1][0]) is _type_SIO:
                fd, l = self.line[-1]
                m = fd.tell()
                fd.seek(0, 2)
                fd.write(d)
                fd.seek(m)
                self.line[-1] = [fd, l + len(d)]
            else:
                self.line.append([make_SIO(d), len(d)])
        else:
            self.line.append([d, get_file_length(d)])

    def close_request(self):
        '''Add a close request to the outgoing pipeline.

        No more data will be allowed in the pipeline, and, when
        it is emptied, PipelineCloseRequest will be raised.
        '''
        self.want_close = True

    def read(self, amt):
        '''Read up to `amt` bytes off the pipeline.

        May raise PipelineCloseRequest if the pipeline is
        empty and the connected stream should be closed.
        '''
        if self.line == [] and self.want_close:
            raise PipelineCloseRequest

        rbuf = []
        read = 0
        while self.line and read < amt:
            data = self.line[0][0].read(amt - read)
            if data == '':
                del self.line[0]
            else:
                rbuf.append(data)
                read += len(data)

        while self.line and self.line[0][1] == self.line[0][0].tell():
            del self.line[0]

        return ''.join(rbuf)
    
    def backup(self, d):
        '''Pop object d back onto the front the pipeline.

        Used in cases where not all data is sent() on the socket,
        for example--the remainder will be placed back in the pipeline.
        '''
        self.line.insert(0, [make_SIO(d), len(d)])

    @property
    def empty(self):
        '''Is the pipeline empty?

        A close request is "data" that needs to be consumed,
        too.
        '''
        return self.want_close == False and self.line == []
