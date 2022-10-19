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


def draw_horizontal_elements(drawing: schemdraw.Drawing,
                            graph_meta_data: pd.DataFrame) -> None:
    '''
    Utility function that draws 2-3 elements for the passed graph meta data record from left to right onto the passed
    drawing object:
    - circle with graph index (optional - not done for root function)
    - rounded box with function's handle label
    - box with function's source module import path
    Returns:

    '''

    drawn_graph_data_list = []

    for graph_meta_data_record in graph_meta_data.itertuples():

        logger.debug(f'Processing flow chart element sequence: {graph_meta_data_record}')

        drawn_graph_data_record = {'target_function_graph_index': graph_meta_data_record.target_function_graph_index}

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

        drawing.add(function_handle_box)

        # add the drawn rounded box to the record for later reference - needed to draw vertical arrows
        drawn_graph_data_record['function_handle_node'] = function_handle_box

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

        drawing.add(function_module_info_box)

        # draw the line between middle and last element
        second_line = flow.Line().at(function_handle_box.E).to(function_module_info_box.W)
        drawing.add(second_line)

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

            drawing.add(function_graph_index_circle)

            # draw the line between first and middle element
            second_line = flow.Line().at(function_graph_index_circle.E).to(function_handle_box.W)
            drawing.add(second_line)

            # add the drawn circle to the record for later reference - needed to draw vertical arrows
            drawn_graph_data_record['graph_index_node'] = function_graph_index_circle

        drawn_graph_data_list.append(drawn_graph_data_record)

    drawn_graph_data = pd.DataFrame(drawn_graph_data_list)

    drawn_graph_meta_data = graph_meta_data.merge(drawn_graph_data,
                                                  how='left',
                                                  on='target_function_graph_index')


    return drawn_graph_meta_data

def get_next_graph_index_nested(graph_index: str) -> str:
    '''
    Utility function that generates the next, nested graph index number for a given graph index. i.e., for
    - '1.2', this function returns '1.2.1'
    - '2.7', this function returns '2.7.1'
    - '1', this function returns '1.1'
    - '3.1.2.2', this function returns '3.1.2.2.1'

    Args:
        graph_index:

    Returns:

    '''

    if graph_index:
        next_graph_index = f'{graph_index}.1'
    else:
        next_graph_index = '1'

    return next_graph_index

def get_next_graph_index_sequential(graph_index: str) -> str:
    '''
    Utility function that generates the next, sequential graph index number for a given graph index. i.e., for
    - '1.2', this function returns '1.3'
    - '2.7', this function returns '2.8'
    - '1', this function returns '2'
    - '3.1.2.2', this function returns '3.1.2.3'

    Args:
        graph_index:

    Returns:

    '''

    # generation 2 and above
    if '.' in graph_index:
        fixed_generations = '.'.join(graph_index.split('.')[:-1])
        next_graph_index = f'{fixed_generations}.{int(graph_index.split(".")[-1])+1}'
    # generation 1
    elif graph_index:
        next_graph_index = str(int(graph_index) + 1)
    else:
        next_graph_index = 'n/a'

    return next_graph_index

def draw_vertical_elements(drawing: schemdraw.Drawing,
                           drawn_graph_meta_data: pd.DataFrame) -> None:
    '''
    Utility function that draws all vertical arrows between the circular graph index nodes on the passed drawing
    objects, using the passed graph_meta_data table

    The logic is as follows: For each generation of horizontal records, we connect the subsequent graph index nodes
    where the graph indices of the leading generation_index-1 entries align. For example:
    - in the first generation, all subsequent graph index nodes (i.e. '1' and '2', '2' and '3' etc) will be connected
    - in the second generation, the following nodes will be connected:
        - '1.1' and '1.2' (leading one entry aligns, and trailing entries are sequential)
        - '2.13' and '2.14' (leading one entry aligns, and trailing entries are sequential)
        - '4.7' and '4.8' (leading one entry aligns, and trailing entries are sequential)
        but the following won't be connected:
        - '1.1' and '2.1' (leading one entry differs)
        - '2.13' and '2.15' (leading one entry differs, but trailing entries are not sequential)
    - in the third generation, the following nodes will be connected:
        - '1.1.1' and '1.1.2'
        - '1.3.4' and '1.3.5'
        - '3.2.7' and '3.2.8'
        but the following won't be connected:
        - '1.1.1' and '1.2.2' (leading two entries '1.1' differ from '1.2')
        - '2.3.1' and '2.4.1' (leading two entries '2.3' differ from '2.4' and trailing entry '1' and '1' are not identical, not sequential)
        - '5.3.2' and '5.3.4' (leading two entries '5.3' align with '5.23', but trailing entry '2' and '4' are not sequential)
    etc.

    Args:
        drawing:
        graph_meta_data:

    Returns:

    '''


    for graph_meta_data_record in drawn_graph_meta_data.itertuples():

        # cover the vertical arrows going from e.g. '1.2' -> '1.2.1'
        next_graph_index_nested = get_next_graph_index_nested(graph_meta_data_record.target_function_graph_index)

        if next_graph_index_nested in drawn_graph_meta_data.target_function_graph_index.tolist():
            logger.debug(f'Next graph index (nested): {next_graph_index_nested}')

            next_graph_meta_data_record = drawn_graph_meta_data.loc[
                drawn_graph_meta_data.target_function_graph_index == next_graph_index_nested]

            # draw arrow from function handle box of current record to graph index circle of next record
            current_node = graph_meta_data_record.function_handle_node
            next_node = next_graph_meta_data_record.graph_index_node.values[0]

            logger.debug(f'Drawing vertical element from {current_node} to {next_node}')

            # draw the vertical arrow element between the identified nodes
            vertical_arrow = flow.Arrow().at(current_node.S).to(next_node.N)
            drawing.add(vertical_arrow)

        # cover the vertical arrows going from e.g. '1.2' -> '1.3'
        next_graph_index_sequential = get_next_graph_index_sequential(
            graph_meta_data_record.target_function_graph_index)

        if next_graph_index_sequential in drawn_graph_meta_data.target_function_graph_index.tolist():
            logger.debug(f'Next graph index (sequential): {next_graph_index_sequential}')

            next_graph_meta_data_record = drawn_graph_meta_data.loc[
                drawn_graph_meta_data.target_function_graph_index == next_graph_index_sequential]

            # draw arrow from graph index circle of current record to graph index circle of next record
            current_node = graph_meta_data_record.graph_index_node
            next_node = next_graph_meta_data_record.graph_index_node.values[0]

            logger.debug(f'Drawing vertical element from {current_node} to {next_node}')

            # draw the vertical arrow element between the identified nodes
            vertical_arrow = flow.Arrow().at(current_node.S).to(next_node.N)
            drawing.add(vertical_arrow)

    return drawing


def plot_project_graph(graph_meta_data: pd.DataFrame) -> schemdraw.Drawing:
    '''
    Utility function that takes in the graph meta data and generates a visualization of the format shown in
    https://miro.com/app/board/uXjVPNNbgDk=/

    Args:
        graph_meta_data:

    Returns:

    '''

    graph_meta_data = add_color_palette(graph_meta_data)

    with schemdraw.Drawing() as drawing:


        drawn_graph_meta_data = draw_horizontal_elements(drawing=drawing,
                                                         graph_meta_data=graph_meta_data)

        logger.debug(f'Drawn horizontal elements in graph; meta data: {drawn_graph_meta_data}')

        full_drawing = draw_vertical_elements(drawing=drawing,
                                              drawn_graph_meta_data=drawn_graph_meta_data)

        logger.debug(f'Drawn vertical and horizontal elements in graph.')


    return full_drawing


