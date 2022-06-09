import gym
import random
import numpy as np

import torch
from torch import optim

from utils import Net
from utils import Buffer


class RL:
    def __init__(self, env):
        self.env = env
        self.net = Net()
        self.net_old = Net()
        self.optimizer = optim.Adam(self.net.parameters(), lr=0.001)
        self.buffer_size = 5000
        self.buffer = Buffer(self.buffer_size)
        self.batch_size = 64
        self.GAMMA = 0.9

    def predict_q(self, status_tensor, net):
        return net.forward(status_tensor)

    def choose_action(self, q_table):
        EPSILON = 0.9
        if random.random() < EPSILON:
            return 0 if q_table[0] > q_table[1] else 1
        else:
            randint = random.randint(0, 1)
            return randint

    def calculate_reward(self, status):
        pos, vel, angle, ang_vel = status
        return 1.0 - abs(pos) - abs(vel) - abs(angle) - abs(ang_vel)

    def update_old_net(self):
        with torch.no_grad():
            for param, old_param in zip(
                self.net.parameters(), self.net_old.parameters()
            ):
                old_param[:] = param.detach()

    def update_net(self):
        loss = 0
        status, action, reward, status_ = self.buffer.random_sample(self.batch_size)
        with torch.no_grad():
            r_, _ = self.predict_q(torch.tensor(status_), self.net_old).max(dim=1)
            y_t = torch.tensor(reward) + self.GAMMA * r_
            # print(y_t[0])

        q_table = self.net.forward(torch.tensor(status))
        q = q_table[list(range(self.batch_size)), action]
        # action is 0 or 1, q_table[action] is the q value of action
        loss = 0.5 * (y_t - q).pow(2).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def rl(self):
        status = self.env.reset()
        # status : position, velocity, angle, angular velocity
        # action : left or right
        # done : boolean, if angle >12 or angle < -12, position < -2.4 or position > 2.4
        i_episode = 1
        min_loss = float("inf")
        max_step = 0
        mean_step = 0

        while True:
            status = env.reset()
            reward_sum = 0
            for t in range(100):
                self.env.render()
                q_table = self.predict_q(torch.tensor(status), self.net)
                action = self.choose_action(q_table)
                status_, reward, dead, _ = self.env.step(action)
                reward = self.calculate_reward(status)
                transition = (status, action, reward, status_)
                self.buffer.input(transition)
                loss = self.update_net()

                status = status_

                min_loss = min(min_loss, loss)
                max_step = max(max_step, t)

                reward_sum += reward

                if dead:
                    mean_step = (mean_step * i_episode + t) / (i_episode + 1)
                    print(f"episode {i_episode} :")
                    print(f"Dead after {t+1} timesteps")
                    print(f"Mean {mean_step} timesteps")
                    print(f"loss: {loss} ", end="")
                    print(f"min loss = {min_loss}, max step = {max_step}")
                    print("q_table:")
                    print(q_table)
                    print(f"reward sum = {reward_sum} \n\n")
                    break

            i_episode += 1
            if i_episode % 100 == 0:
                self.update_old_net()


if __name__ == "__main__":
    env = gym.make("CartPole-v1")
    rl = RL(env)
    rl.rl()
