# from env.matrix_env import MatrixEnv
from env.tagging import TaggingEnv
from env.grid_world import GridEnv
from npa_controller_torch import NaiveController
# import seaborn as sns
# import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from decimal import Decimal
from common.path_utils import *
import joblib
import argparse
import time


ppo_agent_cnt = 0
pac_agent_cnt = 0


def parse_args():
    parser = argparse.ArgumentParser(description="Run tagging game.")

    parser.add_argument('--agent', type=str, default="ppo")
    parser.add_argument('--episodes', type=int, default=100)
    parser.add_argument('--n-steps', type=int, default=20)
    parser.add_argument('--n-belief', type=int, default=10)
    parser.add_argument('--steps-per-round', type=int, default=5)
    parser.add_argument('--prior', type=float, nargs='+', default=[0.5, 0.5])
    parser.add_argument('--learning-rate', type=float, default=5e-5)
    parser.add_argument('--test-every', type=int, default=100)
    parser.add_argument('--save-every', type=int)
    parser.add_argument('--load', action="store_true")
    parser.add_argument('--random-prior', action="store_true")
    parser.add_argument('--load-step', type=int)
    parser.add_argument('--max-steps', type=int, default=1000)
    parser.add_argument('--network-width', type=int, default=32)
    parser.add_argument('--network-depth', type=int, default=2)
    parser.add_argument('--sub-load-path', type=str)
    parser.add_argument('--timesteps-per-batch', type=int, default=8)
    parser.add_argument('--iterations-per-round', type=int, default=16)
    parser.add_argument('--exp-name', type=str)
    parser.add_argument('--other', type=str, default='')
    parser.add_argument('--seed', type=int, default=377)

    return parser.parse_args()

if __name__ == "__main__":

    def argument_to_tuple(argument):
        if type(argument) == list and len(argument) == 1:
            return argument[0]
        elif type(argument) == str:
            return argument
        else:
            parameters = list(map(float, argument[1:]))
            return tuple(argument[:1] + parameters)

    args = parse_args()

    # seed = "benchmark"
    agent = args.agent
    n_steps = args.n_steps
    steps_per_round = args.steps_per_round
    prior = args.prior
    lr = learning_rate = args.learning_rate
    # schedule = ("wolf_adv", 20.0)
    test_every = args.test_every
    save_every = args.save_every
    load = args.load
    load_step = args.load_step
    max_steps = args.max_steps
    network_width = args.network_width
    network_depth = args.network_depth
    timesteps_per_batch = args.timesteps_per_batch
    iterations_per_round = args.iterations_per_round
    betas = [[0.9, 0.99], [0.9, 0.99]]
    gamma = 0.95
    max_episodes = args.episodes
    clip_eps = 0.2
    n_belief = args.n_belief

    # other = "1000-test-steps-large-network"

    result_folder = "../result/"
    plot_folder = "../plots/"
    exp_name = args.exp_name or \
        "_".join(["deceive" + str(args.other),
                  "recurrent",
                  agent,
                  "game:{}-{}-{}".format(n_steps, steps_per_round, ":".join(map(str, prior)) if not args.random_prior else "random"),
                  "{:.0e}".format(Decimal(learning_rate)),
                  "test_every:{}".format(test_every),
                  "network:{}-{}".format(network_width, network_depth),
                  "train:{}*{}".format(timesteps_per_batch, iterations_per_round),
                  "start:{}".format(time.time())])

    exp_dir = os.path.join(result_folder, exp_name)
    plot_dir = os.path.join(plot_folder, exp_name)

    train = True

    res = {"episode": [], "current_assessments": [], "player": []}

    env = GridEnv(n_steps=n_steps, prior=prior)
    # env.export_payoff("/home/footoredo/playground/REPEATED_GAME/EXPERIMENTS/PAYOFFSATTvsDEF/%dTarget/inputr-1.000000.csv" % n_slots)
    if train:
        controller = NaiveController(env, max_episodes, lr, betas, gamma, clip_eps, n_steps, network_width, test_every, n_belief, args.seed)
        controller.train(round_each_belief=1000)
    
