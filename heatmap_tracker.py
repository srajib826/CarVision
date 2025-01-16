import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import seaborn as sns
from collections import deque
from scipy.stats import pearsonr


fig, ax = plt.subplots()

def find_subsets_within_diff(values, diff):
    values.sort()
    subsets = []
    used_values = set()

    for i in range(len(values)):
        if values[i] in used_values:
            continue
        
        current_subset = [values[i]]
        for j in range(i + 1, len(values)):
            if abs(values[j] - values[i]) <= diff:
                current_subset.append(values[j])
                used_values.add(values[j])
            else:
                break
        
        subsets.append(current_subset)
        used_values.add(values[i])

    return subsets


def update(frame):
    ax.clear()

    sns.heatmap(frame[0], ax=ax, cbar=False)
    for peak in frame[1]:
        ax.axvline(x=peak, color='r', linestyle='--')
    

if __name__ == "__main__":
    DOPPLER_RESOLUTION=0.9
    filename = 'day5_combined_obd_mmwave.pickle'
    df = pd.read_pickle(filename)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.sort_values(by='datetime', inplace=True)
    df.reset_index(drop=True, inplace=True)

    threshold = pd.Timedelta(seconds=1)
    continuous_chunks = []
    current_chunk = [df.iloc[0]]

    for i in range(1, len(df)):
        if (df['datetime'].iloc[i] - df['datetime'].iloc[i - 1]) <= threshold:
            current_chunk.append(df.iloc[i])
        else:
            if len(current_chunk) > 1:
                continuous_chunks.append(pd.DataFrame(current_chunk))
            current_chunk = [df.iloc[i]]

    if len(current_chunk) > 1:
        continuous_chunks.append(pd.DataFrame(current_chunk))

    new_df = continuous_chunks[0]
    doppz = np.array(df['doppz'].values.tolist())
    heatmaps = doppz
    prev_indices = []
    final_peaks = []
    range_doppler_velocity = []
    for i, heatmap in enumerate(heatmaps):
        heatmap1 = heatmap.sum(axis=0)
        max_value = np.max(heatmap1)
        threshold = 0.88 * max_value
        
        row_peaks, power_vals = find_peaks(heatmap1, height=threshold)
        filtered_peaks = [peak for peak in row_peaks if 10 <= peak <= 240]

        if len(prev_indices) == 0:
            prev_indices = filtered_peaks
            continue
        
        unique_peaks = []
        for peak in filtered_peaks:
            if any(abs(peak - prev_peak) <= 3 for prev_peak in prev_indices):
                unique_peaks.append(peak)
        
        if unique_peaks:
            prev_indices = unique_peaks
        
        result = find_subsets_within_diff(unique_peaks, 10)
        
        current_final_peaks = [
            sorted(list(map(lambda e: (e, power_vals['peak_heights'][list(row_peaks).index(e)]), peak_set)), key=lambda e: e[1])[-1][0]
            for peak_set in result
        ]
        for peak_index in current_final_peaks:
            top_dop_index = np.argmax(heatmap[:,peak_index])
            if top_dop_index > 8:    
                range_doppler_velocity.append((top_dop_index-8)*DOPPLER_RESOLUTION*(-1))
            elif top_dop_index == 7:
                range_doppler_velocity.append(0)
            else:
                range_doppler_velocity.append((8-top_dop_index)*DOPPLER_RESOLUTION)
        final_peaks.append((heatmap, current_final_peaks))

    plt.plot(range_doppler_velocity)
    plt.show()
    # ani = FuncAnimation(fig, update, frames=final_peaks, repeat=False)
    # mywriter = animation.PillowWriter(fps=5)
    # save_anim_name = filename.split('.')[0]+'_10_3_65.gif'
    # ani.save(save_anim_name, writer=mywriter)

    merged_df = pd.read_pickle("day5_combined_obd_mmwave.pickle")

    velocity_gd = list(merged_df['rel_speed'])    
    datetime_arr = merged_df['datetime'].values.astype(str)

    vel_gt_queue, vel_rd_queue = deque(maxlen=30), deque(maxlen=30)
    max_correlation = -10
    min_correlation = 100
    counter = 0
    correlation_dict_list = []
    max_correlation_dict_list = []
    min_correlation_dict_list = []
    for gt, est, time_val in zip(velocity_gd, range_doppler_velocity, datetime_arr):
        vel_gt_queue.append(gt)
        vel_rd_queue.append(est)
        counter+=1
        if len(vel_rd_queue) < 30:
            continue
        correlation, p_value = pearsonr(vel_gt_queue, vel_rd_queue)
        if p_value < 0.0005:
            correlation_dict = {'counter': counter, 'correlation': correlation, 'p_value': p_value, 'time_val': time_val}
            correlation_dict_list.append(correlation_dict)             
            if max_correlation < correlation:
                max_correlation = correlation
                max_correlation_dict_list.append(correlation_dict)
            if min_correlation > correlation:
                min_correlation = correlation
                min_correlation_dict_list.append(correlation_dict)


    correlations = [d_r['correlation'] for d_r in correlation_dict_list]
    sns.violinplot(y=correlations)
    plt.grid()
    plt.ylabel('Correlation')
    plt.tight_layout()
    plt.savefig('pearson_processed.pdf')
    plt.show()