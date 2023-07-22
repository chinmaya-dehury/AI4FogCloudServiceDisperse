import os
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from h_configs import MODEL_FOLDER, MODEL_OUTPUT_PATH, DynamicParams

class DRLModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.Sigmoid(),
            nn.Linear(hidden_size, output_size),
        )
    def forward(self, x):
        return self.model(x)

    def save(self):
        if not os.path.exists(MODEL_FOLDER):
            os.mkdir(MODEL_FOLDER)
        model_id = datetime.now().strftime("%Y_%m_%d_%H_%M")
        model_name = MODEL_OUTPUT_PATH.format(MODEL_FOLDER, DynamicParams.get_params()['service_type'], (DynamicParams.get_params()['service_count']*DynamicParams.get_params()['slice_count']), model_id)
        torch.save(self.state_dict(), model_name)

class DRLTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        self.loss = None

    def train(self, state_old, action, reward, done, state_new):
        state_old = torch.tensor(state_old, dtype=torch.float)
        state_new = torch.tensor(state_new, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state_old.shape) == 1:
            state_old = torch.unsqueeze(state_old, 0)
            state_new = torch.unsqueeze(state_new, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        pred = self.model(state_old)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(state_new[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
 
        loss.backward()

        self.optimizer.step()

        self.loss = loss.detach().numpy()
