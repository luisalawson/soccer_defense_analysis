import unittest
from src.utils.data_processing import load_data
from src.services.season_service import  process_season_data

class TestMatchMatrix(unittest.TestCase):

    def setUp(self):
        """ Configurar datos de prueba y matriz de referencia """
        self.df = load_data('src/data/matchData.csv')
        self.seasons, self.matches = process_season_data(self.df)

        # Esta sería una matriz de referencia manualmente generada desde la imagen
        # Puedes modificar y completar esto con los resultados de la imagen
        self.expected_matrix = [
    #         ARS         AVL         CHE         EVE         FUL         LIV         MCI         MUN         NEW         NOR         QPR         REA         SOU         STK         SUN         SWA         TOT         WBA         WHU         WIG
    [ None,    (2, 1),    (1, 2),    (0, 0),    (3, 3),    (2, 2),    (0, 2),    (1, 1),    (1, 1),    (7, 3),    (3, 1),    (1, 0),    (4, 1),    (6, 1),    (1, 0),    (0, 0),    (5, 2),    (2, 0),    (5, 1),    (4, 1) ],  # Arsenal
    [(0, 0),   None,      (1, 2),    (1, 3),    (1, 0),    (1, 2),    (1, 2),    (2, 3),    (1, 2),    (1, 1),    (3, 2),    (2, 1),    (0, 1),    (1, 4),    (0, 0),    (0, 0),    (0, 4),    (1, 1),    (2, 0),    (2, 3) ],  # Aston Villa
    [(2, 1),   (8, 0),    None,      (2, 1),    (0, 0),    (2, 1),    (0, 1),    (2, 3),    (3, 2),    (4, 1),    (0, 1),    (4, 2),    (2, 2),    (2, 1),    (1, 0),    (1, 1),    (2, 2),    (2, 1),    (2, 0),    (1, 0) ],  # Chelsea
    [(1, 1),   (3, 3),    (1, 2),    None,      (1, 0),    (2, 2),    (0, 2),    (0, 2),    (1, 2),    (2, 1),    (2, 0),    (1, 2),    (3, 1),    (1, 0),    (1, 0),    (0, 0),    (2, 2),    (2, 0),    (2, 1),    (2, 1) ],  # Everton
    [(0, 1),   (1, 0),    (0, 3),    (2, 2),    None,      (1, 3),    (1, 2),    (0, 1),    (1, 1),    (2, 1),    (3, 2),    (2, 4),    (1, 1),    (0, 1),    (1, 3),    (1, 2),    (0, 3),    (3, 2),    (3, 1),    (1, 1) ],  # Fulham
    [(0, 2),   (1, 3),    (2, 2),    (2, 2),    (4, 0),    None,      (2, 2),    (1, 2),    (0, 1),    (5, 0),    (3, 0),    (1, 3),    (0, 1),    (0, 0),    (1, 0),    (0, 0),    (3, 2),    (4, 1),    (0, 3),    (3, 2) ],  # Liverpool
    [(1, 1),   (5, 0),    (2, 0),    (1, 0),    (2, 0),    (2, 2),    None,      (2, 3),    (4, 0),    (2, 3),    (3, 1),    (1, 0),    (3, 1),    (3, 0),    (3, 0),    (0, 0),    (2, 1),    (5, 0),    (2, 1),    (3, 0) ],  # Manchester City
    [(2, 1),   (3, 0),    (0, 1),    (2, 0),    (3, 2),    (2, 1),    (1, 2),    None,      (4, 3),    (4, 0),    (3, 1),    (1, 0),    (2, 1),    (2, 0),    (3, 1),    (2, 1),    (1, 2),    (2, 0),    (1, 0),    (4, 0) ],  # Manchester United
    [(0, 0),   (1, 1),    (3, 2),    (1, 0),    (1, 3),    (0, 6),    (4, 3),    (0, 3),    None,      (1, 0),    (2, 1),    (0, 1),    (1, 2),    (1, 0),    (1, 1),    (0, 3),    (1, 2),    (1, 2),    (0, 1),    (2, 2) ],  # Newcastle United
    [(1, 0),   (1, 2),    (0, 1),    (2, 1),    (0, 0),    (2, 5),    (3, 4),    (1, 0),    (0, 0),    None,      (1, 1),    (2, 2),    (1, 1),    (1, 0),    (1, 2),    (1, 1),    (2, 1),    (4, 0),    (2, 1),    (1, 2) ],  # Norwich City
    [(0, 1),   (1, 1),    (0, 0),    (2, 0),    (2, 1),    (0, 3),    (2, 2),    (0, 3),    (0, 6),    (2, 3),    None,      (1, 0),    (1, 2),    (0, 0),    (1, 2),    (1, 2),    (1, 2),    (2, 1),    (1, 1),    (1, 3) ],  # Queens Park Rangers
    [(2, 5),   (1, 2),    (2, 2),    (0, 3),    (3, 3),    (0, 3),    (0, 2),    (0, 2),    (1, 0),    (3, 4),    (1, 1),    None,      (0, 0),    (0, 0),    (0, 0),    (0, 0),    (1, 3),    (2, 1),    (0, 0),    (0, 2) ],  # Reading
    [(1, 1),   (4, 1),    (2, 1),    (3, 1),    (0, 1),    (3, 1),    (1, 3),    (2, 3),    (2, 1),    (1, 1),    (1, 2),    (1, 1),    None,      (3, 3),    (1, 1),    (1, 1),    (0, 1),    (3, 0),    (0, 1),    (0, 2) ],  # Southampton
    [(0, 0),   (1, 3),    (0, 1),    (1, 1),    (3, 0),    (0, 0),    (3, 3),    (2, 0),    (1, 2),    (0, 0),    (0, 0),    (0, 2),    (3, 3),    None,      (0, 0),    (0, 2),    (2, 1),    (0, 0),    (0, 1),    (2, 2) ],  # Stoke City
    [(0, 1),   (0, 1),    (1, 3),    (1, 1),    (3, 3),    (3, 0),    (0, 3),    (0, 1),    (1, 1),    (1, 0),    (0, 0),    (2, 2),    (1, 2),    (3, 1),    None,      (0, 0),    (3, 4),    (0, 0),    (1, 0),    (0, 3) ],  # Sunderland
    [(0, 2),   (2, 2),    (2, 1),    (1, 0),    (3, 0),    (0, 0),    (0, 3),    (1, 0),    (1, 1),    (2, 2),    (1, 1),    (0, 0),    (0, 0),    (0, 2),    (3, 1),    None,      (1, 2),    (3, 2),    (3, 1),    (2, 3) ],  # Swansea City
    [(2, 1),   (2, 0),    (2, 4),    (0, 2),    (1, 1),    (3, 2),    (3, 1),    (1, 3),    (1, 2),    (1, 1),    (1, 2),    (3, 3),    (2, 1),    (2, 1),    (2, 1),    (1, 2),    None,      (1, 0),    (3, 2),    (3, 2) ],  # Tottenham Hotspur
    [(2, 1),   (1, 2),    (2, 2),    (0, 2),    (3, 0),    (1, 0),    (1, 2),    (5, 5),    (3, 2),    (3, 1),    (2, 1),    (1, 3),    (3, 0),    (0, 0),    (1, 2),    (2, 1),    (2, 2),    None,      (1, 0),    (1, 1) ],  # West Bromwich Albion
    [(1, 3),   (1, 0),    (3, 1),    (1, 2),    (3, 0),    (0, 0),    (0, 0),    (2, 3),    (0, 1),    (2, 0),    (1, 1),    (0, 0),    (1, 1),    (0, 1),    (1, 0),    (0, 0),    (2, 3),    (3, 1),    None,      (4, 1) ],  # West Ham United
    [(0, 1),   (2, 2),    (0, 2),    (2, 2),    (2, 2),    (0, 3),    (0, 2),    (1, 2),    (2, 2),    (2, 1),    (1, 1),    (0, 2),    (2, 2),    (2, 2),    (3, 1),    (2, 2),    (2, 2),    (1, 1),    (1, 2),    None   ]   # Wigan Athletic
]


    def test_result_matrix(self):
        """ Test para comparar la matriz generada con la esperada """

        # Crear diccionario para mapear equipos a índices
        teams = set()
        for match in self.matches:
            teams.add(match.home_team)
            teams.add(match.away_team)

        # Ordenar equipos alfabéticamente
        sorted_teams = sorted(teams)

        # Mapear equipos a índices
        team_to_index = {team: idx for idx, team in enumerate(sorted_teams)}
        num_teams = len(sorted_teams)

        # Inicializar la matriz de resultados generada por el código
        result_matrix = [[None] * num_teams for _ in range(num_teams)]

        # Llenar la matriz con los resultados de los partidos
        for match in self.matches:
            home_team_idx = team_to_index[match.home_team]
            away_team_idx = team_to_index[match.away_team]
            result_tuple = (match.home_goals, match.away_goals)

            result_matrix[home_team_idx][away_team_idx] = result_tuple

        # Comparar la matriz generada con la matriz esperada
        for i in range(num_teams):
            for j in range(num_teams):
                with self.subTest(home_team=sorted_teams[i], away_team=sorted_teams[j]):
                    self.assertEqual(result_matrix[i][j], self.expected_matrix[i][j])

if __name__ == '__main__':
    unittest.main()


