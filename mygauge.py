from datetime import datetime


class MyGauge:

    def __init__(self, curr = 0, max = 100, steps = 10, waypoint: str = 'start'):

        self._curr = curr
        self._max = max
        self._steps = 10

        self._start = datetime.now()
        self._now = datetime.now()

        self._waypoint = waypoint

    def next():
        pass

    def eta():
        pass

    def eto():
        '''
        Estimated Time Over (ETO)
        Calcula o tempo estimado de voo sobre um determinado ponto.
        No contexto de processamento, estima quanto tempo o passo atual demorará para ser concluído.
        ETO = TAS
        '''
        pass
    
    def ft():
        # Flight/Flying Time: tempo total de voo em segundos
        # ft = now - start
        pass

    def tas():
        # True AirSpeed: velocidade verdadeira em passos por segundo
        # tas = curr / ft
        pass

    def tslp():
        # time since last waypoint".
        pass

    def kts():
        pass