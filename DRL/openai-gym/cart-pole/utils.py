import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        # input: status
        # output: one-hot action vector
        self.fc1 = nn.Linear(4, 64)
        self.fc2 = nn.Linear(64, 16)
        self.fc3 = nn.Linear(16, 2)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)

        return x


# buffer with fixed size
class Buffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.status_buffer = np.empty([self.buffer_size, 4], dtype=np.float32)
        self.action_buffer = np.empty(self.buffer_size, dtype=int)
        self.reward_buffer = np.empty(self.buffer_size, dtype=np.float32)
        self.new_status_buffer = np.empty([self.buffer_size, 4], dtype=np.float32)
        self.index = 0  # new arrived transition

    def input(self, transition: tuple):
        if self.index >= self.buffer_size:
            self.index = 0

        status, action, reward, status_ = transition
        self.status_buffer[self.index, :] = status
        self.action_buffer[self.index] = action
        self.reward_buffer[self.index] = reward
        self.new_status_buffer[self.index, :] = status_

        self.index += 1

    def random_sample(self, batch_size):
        random_choice = np.random.choice(self.buffer_size, batch_size)
        random_status = self.status_buffer[random_choice, :]
        random_actionss = self.action_buffer[random_choice]
        random_rewards = self.reward_buffer[random_choice]
        random_status_ = self.new_status_buffer[random_choice, :]

        return random_status, random_actionss, random_rewards, random_status_


if __name__ == "__main__":
    # test
    buffer = Buffer(10)
    for i in range(12):
        buffer.input(([i, 0, 0, 0], i, i, [i, 1, 1, 1]))

    print(buffer.random_sample(3))
