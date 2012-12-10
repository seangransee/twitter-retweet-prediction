# helper functions

def theilsen(samples):
    N = len(samples)

    def slope(i, j):
        xi, yi = samples[i]
        xj, yj = samples[j]
        if xi - xj:
          return (yi - yj) / (xi - xj)
        else:
          return 0

    def median(L):
      L.sort()
      if len(L) & 1:
          return L[len(L)//2]
      else:
          return (L[len(L)//2] + L[len(L)//2 + 1])/2

    m = median([slope(i,j) for i in range(N) for j in range(i)])

    def error(i):
        x,y = samples[i]
        return y - m*x

    b = median([error(i) for i in range(N)])

    return m,b


def time_to_float(dt):
  import datetime
  return (dt - datetime.datetime(1970, 1, 1)).total_seconds()