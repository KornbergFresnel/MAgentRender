import random
import math
import time

import numpy as np

from env.python.magent import GridWorld


def generate_simple_gw(env: GridWorld, map_size: int, handles: list):
    """Generate grid world map

    Parameters
    ---------
    env: object, environment instance
    map_size: int, grid-world should be a square world, map_size states the width or height
    handles: list, a list includes indicates of groups, elements should be int
    """

    width, height = map_size, map_size
    init_num = map_size * map_size * 0.04
    gap = 3  # the margin of each agent

    if random.random() < 0.5:
        left_id, right_id = 1, 0
    else:
        left_id, right_id = 0, 1

    # === Left settings ===
    side = int(math.sqrt(init_num)) * 2
    pos = []
    for x in range(width // 2 - gap - side, width // 2 - gap, 2):
        for y in range((height - side) // 2, (height - side) // 2 + side, 2):
            pos.append([x, y, 0])
    env.add_agents(handles[left_id], method='custom', pos=pos)

    # === Right settings ===
    pos = []
    for x in range(width // 2 + gap, width // 2 + gap + side, 2):
        for y in range((height - side) // 2, (height - side) // 2 + side, 2):
            pos.append([x, y, 0])
    env.add_agents(handles[right_id], method='custom', pos=pos)


def play(ct: int, env: GridWorld, handles: list, map_size: int, models: list, max_steps=200, train=True, render=False, eps=1.0,
         print_every=20, mode="render", use_parallel=False, local=True):
    """Play a round or train

    Parameters
    ----------
    ct: int
        indicates the time we've enumerated
    env: GridWorld
        environment objection
    handles: list
        contains agent groups' indicators
    map_size: int
        states the size of map with map_size * map_size
    models: list
        contains sub models which extended from BaseModel
    max_steps: int
        indicates the maximum steps
    train: bool
        train or not
    render: bool
        render or not
    eps: float
        when your model is Q-learning, and learning with epsilon-greedy, this argument will make sense
    print_every: int
        define the frequency for
    mode: str, optional
        choices = ["render", "eval"], render default
    """

    env.reset()
    n_groups = len(handles)
    generate_simple_gw(env, map_size, handles)

    if mode == "eval":
        render = False

    step, done, total_reward = 0, False, [0., 0.]
    max_num = [env.get_num(handles[0]), env.get_num(handles[1])]

    ids = [env.get_agent_id(handles[i]) for i in range(n_groups)]

    # record mean reward for each agents
    agent_r_record = [dict(zip(ids[i], [[]] * len(ids[i]))) for i in range(n_groups)]
    sample_start = time.time()

    former_act = [np.zeros(max_num[i]) for i in range(n_groups)]

    while not done and step < max_steps:
        cur_obs = [env.get_observation(handles[i]) for i in range(n_groups)]
        cur_ids = [env.get_agent_id(handles[i]) for i in range(n_groups)]

        if local:
            neighbor_list = [env.get_neighbors(handles[i]) for i in range(n_groups)]

        fake_ids = [cur_ids[i] % max_num[i] for i in range(n_groups)]
        if use_parallel:
            for i in range(2):
                models[i].async_action(ids=cur_ids[i], obs=cur_obs[i], eps=eps)
            action = [models[i].fetch_action() for i in range(n_groups)]
        else:
            action = [models[i].act(ids=fake_ids[i], obs=cur_obs[i][0], feat=cur_obs[i][1], 
                        act=former_act[i], eps=eps) for i in range(n_groups)]
            former_act = action

        for i in range(n_groups):
            env.set_action(handles[i], action[i])

        done = env.step()

        rewards = [env.get_reward(handles[i]) for i in range(n_groups)]
        step_reward = [sum(rewards[i]) for i in range(n_groups)]

        # calculate per agent's reward gain
        if mode == "eval":
            for i in range(n_groups):
                for j, agent_id in enumerate(cur_ids[i]):
                    agent_r_record[i][agent_id].append(rewards[i][j])

        total_reward = [total_reward[i] + step_reward[i] for i in range(n_groups)]
        alive = [env.get_alive(handles[i]) for i in range(n_groups)]

        if train:
            models[0].store_transition(ids=fake_ids[0], obs=cur_obs[0][0], feat=cur_obs[0][1], action=action[0],
                                       reward=rewards[0], terminal=alive[0], nei_obs=cur_obs[0][0],
                                       nei_feat=cur_obs[0][1], nei_ids=fake_ids[0])

        if render:
            env.render()

        env.clear_dead()
        nums = [env.get_num(handle) for handle in handles]

        if step % print_every == 0:
            print("[INFO] step: {0:3d} / nums: {1} / rewards: {2} / total-reward: {3}".format(
                step, nums, np.around(step_reward, 2), np.around(total_reward, 2)
            ))

        step += 1

    print("\n[INFO] >>> TIME CONSUMPTION: {0:.3f}".format(
        time.time() - sample_start))

    # analysis reward gain
    if mode == "eval":
        mean_reward_per_agent = [np.mean(list(map(lambda x: np.mean(x), agent_r_record[i]))) for i in range(2)]
        info = {
            'ave_win_rate': [0, 1] if nums[0] < nums[1] else [1, 1],
            'ave_agent_reward': mean_reward_per_agent,
            'ave_total_reward': total_reward
        }
        print('[INFO] #{}, win: {} / ave-agent-reward: {}'.format(ct, info['ave_win_rate'], info['ave_agent_reward']))
        return info
    else:
        return None
