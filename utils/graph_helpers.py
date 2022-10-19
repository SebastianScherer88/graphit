import pandas as pd
import schemdraw
from schemdraw import flow

from settings import (
    logger,
    FLOW_CHART_FONT_SIZE,
    FLOW_CHART_X_STEP_SMALL,
    FLOW_CHART_X_STEP_STANDARD,
    FLOW_CHART_Y_STEP_STANDARD,
    FLOW_CHART_ELEMENT_HEIGHT_STANDARD,
    FLOW_CHART_ELEMENT_WIDTH_STANDARD,
    FLOW_CHART_SIZE_Y,
    FLOW_CHART_CIRCLE_COLOR,
    FLOW_CHART_COLOR_PALETTE
)


def add_color_palette(graph_meta_data: pd.DataFrame):
    '''
    Utility function that adds a module file based color from the specified color palette to each record in the graph
    meta data.

    In future, can also add meta data specifying the coordinates of plot elements.

    Args:
        graph_meta_data:

    Returns:

    '''

    color_palette = pd.DataFrame(enumerate(FLOW_CHART_COLOR_PALETTE),
                                 columns=['index','color'])

    logger.debug(f'Using color palette: {color_palette}')

    graph_meta_data_modules = graph_meta_data[['target_function_module_import_path']]. \
        drop_duplicates('target_function_module_import_path'). \
        sort_values('target_function_module_import_path',ascending=True)

    graph_meta_data_modules['index'] = range(len(graph_meta_data_modules))

    graph_meta_data_modules = graph_meta_data_modules.merge(color_palette,
                                                            how='left',
                                                            on='index'). \
        drop('index',axis=1)

    graph_meta_data = graph_meta_data.merge(graph_meta_data_modules,
                                            how='left',
                                            on='target_function_module_import_path')

    logger.debug(f'Graph meta data with added color palette: {graph_meta_data}')

    return graph_meta_data


def draw_horizontal_element(diagram: schemdraw.Drawing,
                            graph_meta_data_record: pd.DataFrame) -> None:
    '''
    Utility function that draws 2-3 elements of each function entry in the flow chart frrom left to right:
    - circle with graph index (optional - not done for root function)
    - rounded box with function's handle label
    - box with function's source module import path
    Returns:

    '''

    # draw the center element of the sequence - the box with the function handle as label
    function_handle_box_position_x = graph_meta_data_record.graph_plot_x_coordinate * FLOW_CHART_X_STEP_STANDARD
    function_handle_box_position_y = FLOW_CHART_SIZE_Y - graph_meta_data_record.graph_plot_y_coordinate * FLOW_CHART_Y_STEP_STANDARD

    function_handle_box = flow.RoundBox(
        w=FLOW_CHART_ELEMENT_WIDTH_STANDARD,
        h=FLOW_CHART_ELEMENT_HEIGHT_STANDARD
    ). \
        fill(graph_meta_data_record.color). \
        at([function_handle_box_position_x, function_handle_box_position_y]). \
        label(
        fontsize=FLOW_CHART_FONT_SIZE,
        label=graph_meta_data_record.target_function_handle
    )

    diagram.add(function_handle_box)

    # draw the third and last element of the sequence - the box with the module and import path information
    function_module_info_box_position_x = function_handle_box_position_x + 1 * FLOW_CHART_X_STEP_STANDARD
    function_module_info_box_position_y = function_handle_box_position_y

    function_module_info_box = flow.Box(
        w=FLOW_CHART_ELEMENT_WIDTH_STANDARD,
        h=FLOW_CHART_ELEMENT_HEIGHT_STANDARD
    ). \
        fill(graph_meta_data_record.color). \
        at([function_module_info_box_position_x, function_module_info_box_position_y]). \
        label(
        fontsize=FLOW_CHART_FONT_SIZE,
        label=graph_meta_data_record.target_function_module_import_path)

    diagram.add(function_module_info_box)

    # draw the line between middle and last element
    second_line = flow.Line().at(function_handle_box.E).to(function_module_info_box.W)
    diagram.add(second_line)

    # for all but the root generation, draw the first element of the sequence - the circle with the graph index
    if graph_meta_data_record.target_function_generation != 0:
        function_graph_index_circle_position_x = function_handle_box_position_x - 1 * FLOW_CHART_X_STEP_SMALL
        function_graph_index_circle_position_y = function_handle_box_position_y

        function_graph_index_circle = flow.Circle(r=FLOW_CHART_ELEMENT_HEIGHT_STANDARD / 2).fill(
            FLOW_CHART_CIRCLE_COLOR).at(
            [function_graph_index_circle_position_x, function_graph_index_circle_position_y]).label(
            fontsize=FLOW_CHART_FONT_SIZE,
            label=graph_meta_data_record.target_function_graph_index,
        )

        diagram.add(function_graph_index_circle)

        # draw the line between first and middle element
        second_line = flow.Line().at(function_graph_index_circle.E).to(function_handle_box.W)
        diagram.add(second_line)

    return

def draw_vertical_arrows() -> None:

    return


def plot_project_graph(graph_meta_data: pd.DataFrame) -> None:
    '''
    Utility function that takes in the graph meta data and generates a visualization of the format shown in
    https://miro.com/app/board/uXjVPNNbgDk=/

    Args:
        graph_meta_data:

    Returns:

    '''

    graph_meta_data = add_color_palette(graph_meta_data)

    with schemdraw.Drawing() as diagram:

        for graph_element_sequence in graph_meta_data.itertuples():

            logger.debug(f'Processing flow chart element sequence: {graph_element_sequence}')

            draw_horizontal_element(diagram=diagram,
                                    graph_meta_data_record=graph_element_sequence)

    return


