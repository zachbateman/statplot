'''
Python module for generating statistical distribution plots.
'''
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns
import pandas
import math
from pprint import pprint as pp



def _bin_order(df):
    return sorted({bin for bin in df.BINS})


def swarmplot(df, ax, bin_order: list=[], max_result: float=0, largest_fontsize: int=17, swarmplot_ylim: list=[]):
    sns.set_style('whitegrid')
    if max_result == 0:
        ax.set_ylim([0, round(_get_upper_bound(df.RESULT.max()))])  # set ylim before plotting to ensure good swarmplot point spacing
    else:
        ax.set_ylim([0, max_result])  # set ylim before plotting to ensure good swarmplot point spacing
    if swarmplot_ylim != []:
        ax.set_ylim(swarmplot_ylim)

    point_size = 80 / (len(df) / len(set(df['BINS'])) + 15) ** 0.6
    ax = sns.swarmplot(x='BINS', y='RESULT', data=df, ax=ax, size=point_size, order=bin_order)
    ax.set_xlabel('')
    ax.set_ylabel('RESULT', fontsize=largest_fontsize * 0.8)
    ax.tick_params(labelsize=10)

    line_width = 0.6
    for i, (tick, text) in enumerate(zip(ax.get_xticks(), ax.get_xticklabels())):
        mean = df[df.BINS == bin_order[i]]['RESULT'].mean()
        ax.plot([tick-line_width/2, tick+line_width/2], [mean, mean], lw=5, color='#444455')

    ax.text(0.04, 0.96, 'Lines Indicate Bin Mean', bbox={'facecolor': '#dfdfee', 'edgecolor': '#444455'}, fontdict={'size': largest_fontsize * 0.7}, transform=ax.transAxes)

    ax.set_xlabel('X Label', fontsize=largest_fontsize * 0.8)

    y_format = axis_formatter(max_result)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(y_format))


def dist_plot(sorted_xy_lists, ax2, bin_order: list=[], max_result: float=0, largest_fontsize: int=17, distplot_xlim: list=[], distplot_xticks: list=[]):

    point_size = 350 / (len([val for xy_list in sorted_xy_lists for val in xy_list]) / len(sorted_xy_lists)) ** 0.6
    max_x = 0
    for i, xy_list in enumerate(sorted_xy_lists):
        x, y = zip(*xy_list)
        ax2.scatter(x, y, s=point_size) #, color='r')
        max_x = max(x) if max(x) > max_x else max_x

    if distplot_xlim == []:
        upper_limit = _get_upper_bound(max_x) if max_result == 0 else max_result
        ax2.set_xlim([0, upper_limit])
    else:
        upper_limit = distplot_xlim[-1]
        ax2.set_xlim(distplot_xlim)

    if distplot_xticks == []:
        ax2.set_xticks([upper_limit / 5 * i for i in range(0, 5)])
    else:
        ax2.set_xticks(distplot_xticks)

    ax2.set_xlabel('RESULT', fontsize=largest_fontsize * 0.8)

    ax2.yaxis.tick_right()
    ax2.set_yticks([i / 10 for i in range(1, 10)])  # arg needs to be a list
    ax2.set_yticklabels(['P90', '', '', '', 'P50', '', '', '', 'P10'])

    x_format = axis_formatter(_get_upper_bound(max_x) if max_result == 0 else max_result) if distplot_xlim == [] else axis_formatter(distplot_xlim[1])
    ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(x_format))

    ax2.xaxis.grid(which='major', alpha=0.8)
    ax2.yaxis.grid(which='major', alpha=0.8)

    legend = ax2.legend(labels=bin_order,
        loc='upper left',
        bbox_to_anchor=(0.02, 1.0),
        frameon=True,
        shadow=True,
        framealpha=1.0,
        fontsize=largest_fontsize * 0.6)
    legend.get_frame().set_facecolor('#eeeeee')
    legend.get_frame().set_edgecolor('#888888')
    for index in range(20):  # arbitrarily large number of tries to cover all scenarios
        try:
            legend.legendHandles[index]._sizes = [point_size]  # specifies size of legend marker
        except:
            pass


def axis_formatter(max_value: float):
    '''
    Returns a string used by matplotlib for formatting axis labels
    "second_arg" is something given to the function... not sure what that's about but don't need it
    '''
    if max_value < 0.1:
        return lambda x, second_arg: '{:,.3f}'.format(x)
    elif max_value < 1:
        return lambda x, second_arg: '{:,.2f}'.format(x)
    elif max_value < 10:
        return lambda x, second_arg: '{:,.1f}'.format(x)
    else:
        return lambda x, second_arg: '{:,.0f}'.format(x)


def _get_upper_bound(num):
    '''Return part way or all the way to next highest "order of magnitude" number'''
    for mag_order in range(0, 10):
        for partial in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
            if num <= partial * (10 ** mag_order):
                return partial * (10 ** mag_order)


def create_plot_objects():
    fig = plt.figure(figsize=[10, 6])
    gs = gridspec.GridSpec(1, 2, width_ratios=[5, 3])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    return fig, ax1, ax2


def make_distplot_data(data):
    return [(val, (i+1)/len(data)) for i, val in enumerate(sorted(x for x in data if x is not None and not math.isnan(x)))]


def distribution_plot(df,
                      title: str='Distribution Plot',
                      bin_col: str='',
                      result_col: str='',
                      bin_order: list=[],
                      max_result: float=0,
                      largest_fontsize: int=17,
                      distplot_xlim: list=[],
                      swarmplot_ylim: list=[],
                      distplot_xticks: list=[]):

    fig, ax1, ax2 = create_plot_objects()

    df['BINS'] = df[bin_col]
    df['RESULT'] = df[result_col]

    bin_order = _bin_order(df) if bin_order == [] else bin_order  # list of unique bins

    swarmplot(df, ax1, bin_order=bin_order, max_result=max_result, swarmplot_ylim=swarmplot_ylim)

    dist_data = []
    for bin in bin_order:
        filtered_data = df[df[bin_col] == bin][result_col].tolist()
        if len(filtered_data) > 0:
            dist_data.append(make_distplot_data(filtered_data))

    dist_plot(dist_data, ax2, bin_order=bin_order, max_result=max_result, distplot_xlim=distplot_xlim, distplot_xticks=distplot_xticks)

    tick_size = largest_fontsize * 0.7
    plt.setp(ax1.get_xticklabels(), fontsize=tick_size)
    plt.setp(ax1.get_yticklabels(), fontsize=tick_size)
    plt.setp(ax2.get_xticklabels(), fontsize=tick_size)
    plt.setp(ax2.get_yticklabels(), fontsize=tick_size)

    fig.suptitle(title, fontsize=largest_fontsize, y=0.96)
    ax1.set_ylabel(result_col, fontsize=largest_fontsize * 0.85)
    ax1.set_xlabel(bin_col, fontsize=largest_fontsize * 0.85)
    ax2.set_xlabel(result_col, fontsize=largest_fontsize * 0.85)

    plt.subplots_adjust(left=0.08, right=0.95, bottom=0.08, top=0.90, wspace=0.10)
    plt.show()



if __name__ == '__main__':
    data = pandas.read_excel('test.xlsx', converters={'col_1': str, 'col_2': str})
    data['BINS'] = data[BIN_COLUMN].tolist()
    distribution_plot(data)
