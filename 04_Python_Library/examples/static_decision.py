"""Static expected-loss illustration, not an empirically estimated probability."""
from handoffx.static import expected_losses,human_threshold

def main():
    print(expected_losses({'continue':.65,'human':.90,'stop':0.0},
                          {'continue':1.,'human':4.,'stop':0.},20.,stop_loss=12.))
    print('Human success threshold:',human_threshold(.65,1.,4.,20.))

if __name__=='__main__':main()
