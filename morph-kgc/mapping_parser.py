""" Morph-KGC """

__author__ = "Julián Arenas-Guerrero"
__copyright__ = "Copyright (C) 2020 Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__version__ = "0.1"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "arenas.guerrero.julian@outlook.com"
__status__ = 'Prototype'


import rdflib
import logging
import sql_metadata
import pandas as pd

import relational_source


MAPPINGS_DATAFRAME_COLUMNS = [
    'source_name',
    'triples_map_id', 'data_source', 'object_map', 'ref_form', 'iterator', 'tablename', 'query',
    'subject_template', 'subject_reference', 'subject_constant', 'subject_rdf_class', 'subject_termtype',
    'graph_constant', 'graph_reference', 'graph_template',
    'predicate_constant', 'predicate_template', 'predicate_reference',
    'object_constant', 'object_template', 'object_reference', 'object_termtype', 'object_datatype', 'object_language',
    'object_parent_triples_map', 'join_conditions',
    'predicate_object_graph_constant', 'predicate_object_graph_reference', 'predicate_object_graph_template'
]


SQL_RDF_DATATYPE = {
    'INTEGER': 'http://www.w3.org/2001/XMLSchema#integer',
    'INT': 'http://www.w3.org/2001/XMLSchema#integer',
    'SMALLINT': 'http://www.w3.org/2001/XMLSchema#integer',
    'DECIMAL': 'http://www.w3.org/2001/XMLSchema#decimal',
    'NUMERIC': 'http://www.w3.org/2001/XMLSchema#decimal',
    'FLOAT': 'http://www.w3.org/2001/XMLSchema#double',
    'REAL': 'http://www.w3.org/2001/XMLSchema#double',
    'DOUBLE': 'http://www.w3.org/2001/XMLSchema#double',
    'BOOL': 'http://www.w3.org/2001/XMLSchema#boolean',
    'TINYINT': 'http://www.w3.org/2001/XMLSchema#boolean',
    'BOOLEAN': 'http://www.w3.org/2001/XMLSchema#boolean',
    'DATE': 'http://www.w3.org/2001/XMLSchema#date',
    'TIME': 'http://www.w3.org/2001/XMLSchema#time',
    'DATETIME': 'http://www.w3.org/2001/XMLSchema#',
    'TIMESTAMP': 'http://www.w3.org/2001/XMLSchema#dateTime',
    'BINARY': 'http://www.w3.org/2001/XMLSchema#hexBinary',
    'VARBINARY': 'http://www.w3.org/2001/XMLSchema#hexBinary',
    'BIT': 'http://www.w3.org/2001/XMLSchema#hexBinary',
    'YEAR': 'http://www.w3.org/2001/XMLSchema#integer'
}


"""This query has been reused from SDM-RDFizer (https://github.com/SDM-TIB/SDM-RDFizer). SDM-RDFizer has been developed
by members of the Scientific Data Management Group at TIB. Its development has been coordinated and supervised by
Maria-Esther Vidal. The implementation has been done by Enrique Iglesias and Guillermo Betancourt under the
supervision of David Chaves-Fraga, Samaneh Jozashoori, and Kemele Endris.
It has been partially modified by the Ontology Engineering Group (OEG) from Universidad Politécnica de Madrid (UPM)."""
RML_MAPPING_PARSING_QUERY = """
    prefix rr: <http://www.w3.org/ns/r2rml#>
    prefix rml: <http://semweb.mmlab.be/ns/rml#>

    SELECT DISTINCT
        ?triples_map_id ?data_source ?ref_form ?iterator ?tablename ?query ?_object_map
        ?subject_template ?subject_reference ?subject_constant
        ?subject_rdf_class ?subject_termtype
        ?graph_constant ?graph_reference ?graph_template
        ?predicate_constant ?predicate_template ?predicate_reference
        ?object_constant ?object_template ?object_reference ?object_termtype ?object_datatype ?object_language
        ?object_parent_triples_map
        ?predicate_object_graph_constant ?predicate_object_graph_reference ?predicate_object_graph_template

    WHERE {
        ?triples_map_id rml:logicalSource ?_source .
        OPTIONAL { ?_source rml:source ?data_source . }
        OPTIONAL { ?_source rml:referenceFormulation ?ref_form . }
        OPTIONAL { ?_source rml:iterator ?iterator . }
        OPTIONAL { ?_source rr:tableName ?tablename . }
        OPTIONAL { ?_source rml:query ?query . }

# Subject -------------------------------------------------------------------------
        OPTIONAL {
            ?triples_map_id rr:subjectMap ?_subject_map .
            OPTIONAL { ?_subject_map rr:template ?subject_template . }
            OPTIONAL { ?_subject_map rml:reference ?subject_reference . }
            OPTIONAL { ?_subject_map rr:constant ?subject_constant . }
            OPTIONAL { ?_subject_map rr:class ?subject_rdf_class . }
            OPTIONAL { ?_subject_map rr:termType ?subject_termtype . }
            OPTIONAL { ?_subject_map rr:graph ?graph_constant . }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:constant ?graph_constant .
            }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:template ?graph_template .
            }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:reference ?graph_reference .
            }
        }
        OPTIONAL { ?triples_map_id rr:subject ?subject_constant . }

# Predicate -----------------------------------------------------------------------
        OPTIONAL {
            ?triples_map_id rr:predicateObjectMap ?_predicate_object_map .
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rr:constant ?predicate_constant .
            }
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rr:template ?predicate_template .
            }
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rml:reference ?predicate_reference .
            }
            OPTIONAL { ?_predicate_object_map rr:predicate ?predicate_constant . }

# Object --------------------------------------------------------------------------
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:constant ?object_constant .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:template ?object_template .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rml:reference ?object_reference .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:parentTriplesMap ?object_parent_triples_map .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:object ?object_constant .
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL { ?_predicate_object_map rr:graph ?predicate_object_graph_constant . }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:constant ?predicate_object_graph_constant .
            }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:template ?predicate_object_graph_template .
            }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:reference ?predicate_object_graph_reference .
            }
        }
    }
"""


R2RML_MAPPING_PARSING_QUERY = """
    prefix rr: <http://www.w3.org/ns/r2rml#>

# RML compliance: ?data_source ?ref_form ?iterator --------------------------------
    SELECT DISTINCT
        ?triples_map_id ?data_source ?ref_form ?iterator ?tablename ?query ?_object_map
        ?subject_template ?subject_reference ?subject_constant
        ?subject_rdf_class ?subject_termtype
        ?graph_constant ?graph_reference ?graph_template
        ?predicate_constant ?predicate_template ?predicate_reference
        ?object_constant ?object_template ?object_reference ?object_termtype ?object_datatype ?object_language
        ?object_parent_triples_map
        ?predicate_object_graph_constant ?predicate_object_graph_reference ?predicate_object_graph_template

    WHERE {
        ?triples_map_id rr:logicalTable ?_source .
        OPTIONAL { ?_source rr:tableName ?tablename . }
        OPTIONAL { ?_source rr:sqlQuery ?query . }

# Subject -------------------------------------------------------------------------
        OPTIONAL {
            ?triples_map_id rr:subjectMap ?_subject_map .
            OPTIONAL { ?_subject_map rr:template ?subject_template . }
            OPTIONAL { ?_subject_map rr:column ?subject_reference . }
            OPTIONAL { ?_subject_map rr:constant ?subject_constant . }
            OPTIONAL { ?_subject_map rr:class ?subject_rdf_class . }
            OPTIONAL { ?_subject_map rr:termType ?subject_termtype . }
            OPTIONAL { ?_subject_map rr:graph ?graph_constant . }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:constant ?graph_constant .
            }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:template ?graph_template .
            }
            OPTIONAL {
                ?_subject_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:column ?graph_reference .
            }
        }
        OPTIONAL { ?triples_map_id rr:subject ?subject_constant . }

# Predicate -----------------------------------------------------------------------
        OPTIONAL {
            ?triples_map_id rr:predicateObjectMap ?_predicate_object_map .
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rr:constant ?predicate_constant .
            }
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rr:template ?predicate_template .
            }
            OPTIONAL {
                ?_predicate_object_map rr:predicateMap ?_predicate_map .
                ?_predicate_map rr:column ?predicate_reference .
            }
            OPTIONAL { ?_predicate_object_map rr:predicate ?predicate_constant . }

# Object --------------------------------------------------------------------------
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:constant ?object_constant .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:template ?object_template .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:column ?object_reference .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:objectMap ?_object_map .
                ?_object_map rr:parentTriplesMap ?object_parent_triples_map .
                OPTIONAL { ?_object_map rr:termType ?object_termtype . }
            }
            OPTIONAL {
                ?_predicate_object_map rr:object ?object_constant .
                OPTIONAL { ?_object_map rr:datatype ?object_datatype . }
                OPTIONAL { ?_object_map rr:language ?object_language . }
            }
            OPTIONAL { ?_predicate_object_map rr:graph ?predicate_object_graph_constant . }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:constant ?predicate_object_graph_constant .
            }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:template ?predicate_object_graph_template .
            }
            OPTIONAL {
                ?_predicate_object_map rr:graphMap ?_graph_structure .
                ?_graph_structure rr:column ?predicate_object_graph_reference .
            }
        }
    }
"""


JOIN_CONDITION_PARSING_QUERY = """
    prefix rr: <http://www.w3.org/ns/r2rml#>

    SELECT DISTINCT ?_object_map ?join_condition ?child_value ?parent_value
    WHERE {
        ?_object_map rr:joinCondition ?join_condition .
        ?join_condition rr:child ?child_value;
                        rr:parent ?parent_value.
    }
"""


def _infer_mapping_language_from_graph(mapping_graph, source_name):
    rml_inferred = False

    # Check if mapping language is RML
    rml_query = '''
        prefix rml: <http://semweb.mmlab.be/ns/rml#>
        SELECT ?s WHERE { ?s rml:logicalSource ?o . } LIMIT 1
    '''
    mapping_language_results = mapping_graph.query(rml_query)
    if len(mapping_language_results) > 0:
        logging.info('RML mapping language inferred for data source ' + source_name + '.')
        rml_inferred = True

    # Check if mapping language is R2RML
    r2rml_query = '''
        prefix rr: <http://www.w3.org/ns/r2rml#>
        SELECT ?s WHERE { ?s rr:logicalTable ?o . } LIMIT 1
    '''
    mapping_language_results = mapping_graph.query(r2rml_query)
    if len(mapping_language_results) > 0:
        logging.info('R2RML mapping language inferred for data source ' + source_name + '.')
        if rml_inferred:
            raise Exception('Both, RML and R2RML were inferred for the mappings for data source ' + source_name)
        else:
            return 'R2RML'

    if rml_inferred:
        return 'RML'

    # If mappings file does not have rml:logicalSource or rr:logicalTable it is not valid
    raise Exception('It was not possible to infer the mapping language for data source ' + source_name +
                    '. Check the corresponding mappings file.')


def _parse_mapping_files(source_options, source_name):
    mapping_graph = rdflib.Graph()
    try:
        for mapping_file in source_options['mapping_files'].split(','):
            mapping_graph.load(mapping_file.strip(), format='n3')
    except Exception as n3_mapping_parse_exception:
        raise Exception(n3_mapping_parse_exception)

    mapping_language = _infer_mapping_language_from_graph(mapping_graph, source_name)
    mapping_parsing_query = ''
    if mapping_language == 'RML':
        mapping_parsing_query = RML_MAPPING_PARSING_QUERY
    elif mapping_language == 'R2RML':
        mapping_parsing_query = R2RML_MAPPING_PARSING_QUERY

    mapping_query_results = mapping_graph.query(mapping_parsing_query)

    join_query_results = mapping_graph.query(JOIN_CONDITION_PARSING_QUERY)
    mappings_df = _transform_mappings_into_dataframe(mapping_query_results, join_query_results, source_name)

    return mappings_df


def _transform_mappings_into_dataframe(mapping_query_results, join_query_results, source_name):
    '''
    Transforms the result from a SPARQL query in rdflib to a DataFrame.

    :param mapping_query_results:
    :return:
    '''

    source_mappings_df = pd.DataFrame(columns=MAPPINGS_DATAFRAME_COLUMNS)
    for mapping_rule in mapping_query_results:
        source_mappings_df = _append_mapping_rule(source_mappings_df, mapping_rule)

    join_conditions_dict = _get_join_object_maps_join_conditions(join_query_results)
    source_mappings_df['join_conditions'] = source_mappings_df['object_map'].map(join_conditions_dict)
    # needed for later hashing the dataframe
    source_mappings_df['join_conditions'] = source_mappings_df['join_conditions'].where(pd.notnull(source_mappings_df['join_conditions']), '')
    source_mappings_df['join_conditions'] = source_mappings_df['join_conditions'].astype(str)
    source_mappings_df.drop('object_map', axis=1, inplace=True)

    source_mappings_df['source_name'] = source_name

    return source_mappings_df


def _get_join_object_maps_join_conditions(join_query_results):
    join_conditions_dict = {}

    for join_condition in join_query_results:
        if join_condition._object_map not in join_conditions_dict:
            join_conditions_dict[join_condition._object_map] = {}

        join_conditions_dict[join_condition._object_map][str(join_condition.join_condition)] = \
            {'child_value': str(join_condition.child_value), 'parent_value': str(join_condition.parent_value)}

    return join_conditions_dict


def _append_mapping_rule(mappings_df, mapping_rule):
    i = len(mappings_df)

    mappings_df.at[i, 'triples_map_id'] = mapping_rule.triples_map_id
    mappings_df.at[i, 'data_source'] = mapping_rule.data_source
    mappings_df.at[i, 'object_map'] = mapping_rule._object_map
    mappings_df.at[i, 'ref_form'] = mapping_rule.ref_form
    mappings_df.at[i, 'iterator'] = mapping_rule.iterator
    mappings_df.at[i, 'tablename'] = mapping_rule.tablename
    mappings_df.at[i, 'query'] = mapping_rule.query
    mappings_df.at[i, 'subject_template'] = mapping_rule.subject_template
    mappings_df.at[i, 'subject_reference'] = mapping_rule.subject_reference
    mappings_df.at[i, 'subject_constant'] = mapping_rule.subject_constant
    mappings_df.at[i, 'subject_rdf_class'] = mapping_rule.subject_rdf_class
    mappings_df.at[i, 'subject_termtype'] = mapping_rule.subject_termtype
    mappings_df.at[i, 'graph_constant'] = mapping_rule.graph_constant
    mappings_df.at[i, 'graph_template'] = mapping_rule.graph_template
    mappings_df.at[i, 'graph_reference'] = mapping_rule.graph_reference
    mappings_df.at[i, 'predicate_constant'] = mapping_rule.predicate_constant
    mappings_df.at[i, 'predicate_template'] = mapping_rule.predicate_template
    mappings_df.at[i, 'predicate_reference'] = mapping_rule.predicate_reference
    mappings_df.at[i, 'object_constant'] = mapping_rule.object_constant
    mappings_df.at[i, 'object_template'] = mapping_rule.object_template
    mappings_df.at[i, 'object_reference'] = mapping_rule.object_reference
    mappings_df.at[i, 'object_termtype'] = mapping_rule.object_termtype
    mappings_df.at[i, 'object_datatype'] = mapping_rule.object_datatype
    mappings_df.at[i, 'object_language'] = mapping_rule.object_language
    mappings_df.at[i, 'object_parent_triples_map'] = mapping_rule.object_parent_triples_map
    mappings_df.at[i, 'predicate_object_graph_constant'] = mapping_rule.predicate_object_graph_constant
    mappings_df.at[i, 'predicate_object_graph_reference'] = mapping_rule.predicate_object_graph_reference
    mappings_df.at[i, 'predicate_object_graph_template'] = mapping_rule.predicate_object_graph_template

    return mappings_df


def _remove_duplicated_mapping_rules(mappings_df):
    ''' Ensure there are no duplicate rules '''

    num_mapping_rules = len(mappings_df)
    mappings_df.drop_duplicates(inplace=True)
    if len(mappings_df) < num_mapping_rules:
        logging.warning('Duplicated mapping rules were found. Ignoring duplicated mapping rules.')

    return mappings_df


def _validate_mapping_partitions(mappings_df, mapping_partitions):
    if 's' in mapping_partitions:
        '''
        Subject is used as partitioning criteria.
        If there is any subject that is a reference that means it is not a template nor a constant, and it cannot
        be used as partitioning criteria.
        '''
        if mappings_df['subject_reference'].notna().any():
            raise Exception('Invalid mapping partitions criteria ' + mapping_partitions + ': mappings cannot be '
                            'partitioned by subject because mappings contain subject terms that are rr:column or '
                            'rml:reference.')
    if 'p' in mapping_partitions:
        '''
        Predicate is used as partitioning criteria.
        If there is any predicate that is a reference that means it is not a template nor a constant, and it cannot
        be used as partitioning criteria.
        '''
        if mappings_df['subject_reference'].notna().any():
            raise Exception('Invalid mapping partitions criteria ' + mapping_partitions +
                            ': mappings cannot be partitioned by predicate because mappings contain predicate terms '
                            'that are rr:column or rml:reference.')
    if 'g' in mapping_partitions:
        '''
        Graph is used as partitioning criteria.
        If there is any graph that is a reference that means it is not a template nor a constant, and it cannot
        be used as partitioning criteria.
        '''
        if mappings_df['graph_reference'].notna().any():
            raise Exception('Invalid mapping partitions criteria ' + mapping_partitions +
                            ': mappings cannot be partitioned by graph because mappings '
                            'contain graph terms that are rr:column or rml:reference.')


def _get_invariable_part_of_template(template):
    zero_width_space = '\u200B'
    template_for_splitting = template.replace('\{', zero_width_space)
    if '{' in template_for_splitting:
        invariable_part_of_template = template_for_splitting.split('{')[0]
        invariable_part_of_template = invariable_part_of_template.replace(zero_width_space, '\{')
    else:
        raise Exception('Invalid string template ' + template + '. No pairs of unescaped curly braces were found.')

    return invariable_part_of_template


def _get_mapping_partitions_invariable_parts(mappings_df, mapping_partitions):
    mappings_df['subject_invariable_part'] = ''
    mappings_df['predicate_invariable_part'] = ''
    mappings_df['graph_invariable_part'] = ''

    for i, mapping_rule in mappings_df.iterrows():
        if 's' in mapping_partitions:
            if mapping_rule['subject_template']:
                mappings_df.at[i, 'subject_invariable_part'] = \
                    _get_invariable_part_of_template(mapping_rule['subject_template'])
            elif mapping_rule['subject_constant']:
                mappings_df.at[i, 'subject_invariable_part'] = mapping_rule['subject_constant']
            else:
                raise Exception('An invalid subject term was found at triples map ' + mapping_rule['triples_map_id'] +
                                '. Subjects terms must be constants or templates in order to generate valid mapping '
                                'partitions by subject.')
        if 'p' in mapping_partitions:
            if mapping_rule['predicate_constant']:
                mappings_df.at[i, 'predicate_invariable_part'] = mapping_rule['predicate_constant']
            elif mapping_rule['predicate_template']:
                mappings_df.at[i, 'predicate_invariable_part'] = \
                    _get_invariable_part_of_template(mapping_rule['predicate_template'])
            else:
                raise Exception('An invalid predicate term was found at triples map ' + mapping_rule['triples_map_id'] +
                                '. Predicate terms must be constants or templates in order to generate valid mapping '
                                'partitions by predicate.')
        if 'g' in mapping_partitions:
            if mapping_rule['graph_constant']:
                mappings_df.at[i, 'graph_invariable_part'] = mapping_rule['graph_constant']
            elif mapping_rule['graph_template']:
                mappings_df.at[i, 'graph_invariable_part'] = \
                    _get_invariable_part_of_template(mapping_rule['graph_template'])
            else:
                raise Exception('An invalid graph term was found at triples map ' + mapping_rule['triples_map_id'] +
                                '. Graph terms must be constants or templates in order to generate valid mapping '
                                'partitions by graph.')

    return mappings_df


def _generate_mapping_partitions(mappings_df, mapping_partitions):
    mappings_df = _get_mapping_partitions_invariable_parts(mappings_df, mapping_partitions)
    mappings_df['subject_partition'] = ''
    mappings_df['predicate_partition'] = ''
    mappings_df['graph_partition'] = ''

    '''
        First generate partitions for subject. Then generate the partitions for predicates. Finally merge both to
        get the final partitions.
    '''

    if 's' in mapping_partitions:
        mappings_df.sort_values(by='subject_invariable_part', inplace=True, ascending=True)
        num_partition = 0
        root_last_partition = 'zzyy xxww\u200B'
        for i, mapping_rule in mappings_df.iterrows():
            if mapping_rule['subject_invariable_part'].startswith(root_last_partition):
                mappings_df.at[i, 'subject_partition'] = str(num_partition)
            else:
                num_partition = num_partition + 1
                root_last_partition = mapping_rule['subject_invariable_part']
                mappings_df.at[i, 'subject_partition'] = str(num_partition)
    if 'p' in mapping_partitions:
        mappings_df.sort_values(by='predicate_invariable_part', inplace=True, ascending=True)
        num_partition = 0
        root_last_partition = 'zzyy xxww\u200B'
        for i, mapping_rule in mappings_df.iterrows():
            if mapping_rule['predicate_invariable_part'].startswith(root_last_partition):
                mappings_df.at[i, 'predicate_partition'] = str(num_partition)
            else:
                num_partition = num_partition + 1
                root_last_partition = mapping_rule['predicate_invariable_part']
                mappings_df.at[i, 'predicate_partition'] = str(num_partition)
    if 'g' in mapping_partitions:
        mappings_df.sort_values(by='graph_invariable_part', inplace=True, ascending=True)
        num_partition = 0
        root_last_partition = 'zzyy xxww\u200B'
        for i, mapping_rule in mappings_df.iterrows():
            if mapping_rule['graph_invariable_part'].startswith(root_last_partition):
                mappings_df.at[i, 'graph_partition'] = str(num_partition)
            else:
                num_partition = num_partition + 1
                root_last_partition = mapping_rule['graph_invariable_part']
                mappings_df.at[i, 'graph_partition'] = str(num_partition)

    ''' generate final partition names '''
    if 's' in mapping_partitions and 'p' in mapping_partitions:
        mappings_df['mapping_partition'] = mappings_df['subject_partition'] + '-' + mappings_df['predicate_partition']
    else:
        mappings_df['mapping_partition'] = mappings_df['subject_partition'] + mappings_df['predicate_partition']
    if 'g' in mapping_partitions and 's' not in mapping_partitions and 'p' not in mapping_partitions:
        mappings_df['mapping_partition'] = mappings_df['graph_partition']
    elif 'g' in mapping_partitions:
        mappings_df['mapping_partition'] = mappings_df['mapping_partition'] + '-' + mappings_df['graph_partition']

    '''' drop the auxiliary columns that are just used to get mapping_partition '''
    mappings_df.drop([
        'subject_partition',
        'predicate_partition',
        'subject_invariable_part',
        'predicate_invariable_part',
        'graph_partition',
        'graph_invariable_part'],
        axis=1, inplace=True)

    logging.info(str(len(set(mappings_df['mapping_partition']))) + ' mapping partitions were generated.')

    return mappings_df


def _get_configuration_and_sources(config):
    """
    Separates the sources from the configuration options.

    :param config: ConfigParser object
    :type config: configparser
    :return: tuple with the configuration options and the sources
    :rtype tuple
    """

    configuration = dict(config.items('CONFIGURATION'))

    data_sources = {}
    for section in config.sections():
        if section != 'CONFIGURATION':
            ''' if section is not configuration then it is a data source.
                Mind that DEFAULT section is not triggered with config.sections(). '''
            data_sources[section] = dict(config.items(section))

    return configuration, data_sources


def  _rdf_class_to_pom(mappings_df):
    '''Transform subject rdf class into separate POM'''

    initial_mapping_df = mappings_df.copy()

    for i, row in initial_mapping_df.iterrows():
        if pd.notna(row['subject_rdf_class']):
            j = len(mappings_df)
            mappings_df.at[j, 'source_name'] = row['source_name']
            # add rdf_class_ at the beginning to avoid problems in later processing
            mappings_df.at[j, 'triples_map_id'] = 'rdf_class_' + str(row['triples_map_id'])
            mappings_df.at[j, 'tablename'] = row['tablename']
            mappings_df.at[j, 'query'] = row['query']
            mappings_df.at[j, 'subject_template'] = row['subject_template']
            mappings_df.at[j, 'subject_reference'] = row['subject_reference']
            mappings_df.at[j, 'subject_constant'] = row['subject_constant']
            mappings_df.at[j, 'graph_constant'] = row['graph_constant']
            mappings_df.at[j, 'graph_reference'] = row['graph_reference']
            mappings_df.at[j, 'graph_template'] = row['graph_template']
            mappings_df.at[j, 'subject_termtype'] = row['subject_termtype']
            mappings_df.at[j, 'predicate_constant'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
            mappings_df.at[j, 'object_constant'] = row['subject_rdf_class']
            mappings_df.at[j, 'object_termtype'] = 'http://www.w3.org/ns/r2rml#IRI'
            mappings_df.at[j, 'join_conditions'] = ''

    mappings_df.drop('subject_rdf_class', axis=1, inplace=True)
    mappings_df.drop_duplicates(inplace=True)

    return mappings_df


def _complete_termtypes(mappings_df):
    for i, mapping_rule in mappings_df.iterrows():
        if pd.isna(mapping_rule['subject_termtype']):
            mappings_df.at[i, 'subject_termtype'] = 'http://www.w3.org/ns/r2rml#IRI'
        if pd.isna(mapping_rule['object_termtype']):
            if pd.notna(mapping_rule['object_language']) or pd.notna(mapping_rule['object_datatype']) or \
                    pd.notna(mapping_rule['object_reference']):
                mappings_df.at[i, 'object_termtype'] = 'http://www.w3.org/ns/r2rml#Literal'
            else:
                mappings_df.at[i, 'object_termtype'] = 'http://www.w3.org/ns/r2rml#IRI'

    return mappings_df


def _set_pom_graphs(mappings_df):
    for i, mapping_rule in mappings_df.iterrows():
        if pd.isna(mapping_rule['graph_constant']) and pd.isna(mapping_rule['graph_reference']) and \
                pd.isna(mapping_rule['graph_template']):
            if pd.isna(mapping_rule['predicate_object_graph_constant']) and \
                    pd.isna(mapping_rule['predicate_object_graph_reference']) and \
                    pd.isna(mapping_rule['predicate_object_graph_template']):
                mappings_df.at[i, 'graph_constant'] = 'http://www.w3.org/ns/r2rml#defaultGraph'

    aux_mappings_df = mappings_df.copy()
    for i, mapping_rule in aux_mappings_df.iterrows():
        if pd.notna(mapping_rule['predicate_object_graph_constant']):
            j = len(mappings_df)
            mappings_df.loc[j] = mapping_rule
            mappings_df.at[j, 'graph_constant'] = mapping_rule['predicate_object_graph_constant']
        if pd.notna(mapping_rule['predicate_object_graph_template']):
            j = len(mappings_df)
            mappings_df.loc[j] = mapping_rule
            mappings_df.at[j, 'graph_template'] = mapping_rule['predicate_object_graph_template']
        if pd.notna(mapping_rule['predicate_object_graph_reference']):
            j = len(mappings_df)
            mappings_df.loc[j] = mapping_rule
            mappings_df.at[j, 'graph_reference'] = mapping_rule['predicate_object_graph_reference']

    mappings_df = mappings_df.drop(columns=['predicate_object_graph_constant', 'predicate_object_graph_template',
                                            'predicate_object_graph_reference'])
    mappings_df = mappings_df.dropna(subset=['graph_constant', 'graph_template', 'graph_reference'], how='all')
    mappings_df.drop_duplicates(inplace=True)

    return mappings_df


def _complete_source_types(mappings_df, config):
    for i, mapping_rule in mappings_df.iterrows():
        mappings_df.at[i, 'source_type'] = config.get(mapping_rule['source_name'], 'source_type').lower()

    return mappings_df


def _is_delimited(value):
    value = str(value)
    if len(value) > 2:
        if value[0] == '"' and value[len(value) - 1] == '"':
            return True
    return False


def _get_valid_identifier_name(name):
    if str(name) != 'nan':
        if _is_delimited(name):
            return name[1:-1]
    return name


def _get_valid_template_identifiers(template):
    if template:
        if str(template) != 'nan':
            return template.replace('{"', '{').replace('"}', '}')
    return template


def _remove_delimiters_from_identifiers(mappings_df):
    for i, mapping_rule in mappings_df.iterrows():
        mappings_df.at[i, 'tablename'] = _get_valid_identifier_name(mapping_rule['tablename'])
        mappings_df.at[i, 'subject_template'] = _get_valid_template_identifiers(mapping_rule['subject_template'])
        mappings_df.at[i, 'subject_reference'] = _get_valid_identifier_name(mapping_rule['subject_reference'])
        mappings_df.at[i, 'graph_reference'] = _get_valid_identifier_name(mapping_rule['graph_reference'])
        mappings_df.at[i, 'graph_template'] = _get_valid_template_identifiers(mapping_rule['graph_template'])
        mappings_df.at[i, 'predicate_template'] = _get_valid_template_identifiers(mapping_rule['predicate_template'])
        mappings_df.at[i, 'predicate_reference'] = _get_valid_identifier_name(mapping_rule['predicate_reference'])
        mappings_df.at[i, 'object_template'] = _get_valid_template_identifiers(mapping_rule['object_template'])
        mappings_df.at[i, 'object_reference'] = _get_valid_identifier_name(mapping_rule['object_reference'])

        if mapping_rule['join_conditions']:
            join_conditions = eval(mapping_rule['join_conditions'])
            for key, value in join_conditions.items():
                join_conditions[key]['child_value'] = _get_valid_identifier_name(join_conditions[key]['child_value'])
                join_conditions[key]['parent_value'] = _get_valid_identifier_name(join_conditions[key]['parent_value'])
                mappings_df.at[i, 'join_conditions'] = str(join_conditions)

    return mappings_df


def _infer_datatypes(mappings_df, config):
    for i, mapping_rule in mappings_df.iterrows():
        if mapping_rule['object_termtype'] == 'http://www.w3.org/ns/r2rml#Literal':
            if pd.isna(mapping_rule['object_datatype']) and pd.isna(mapping_rule['object_language']):
                if pd.notna(mapping_rule['tablename']):
                    data_type = relational_source.get_column_datatype(config, mapping_rule['source_name'],
                                                                      mapping_rule['tablename'],
                                                                      mapping_rule['object_reference']).upper()
                    if data_type in SQL_RDF_DATATYPE:
                        mappings_df.at[i, 'object_datatype'] = SQL_RDF_DATATYPE[data_type]
                elif pd.notna(mapping_rule['query']):
                    table_names = sql_metadata.get_query_tables(mapping_rule['query'])
                    for table_name in table_names:
                        try:
                            data_type = relational_source.get_column_datatype(config, mapping_rule['source_name'],
                                                                          table_name, mapping_rule['object_reference']).upper()
                            if data_type in SQL_RDF_DATATYPE:
                                mappings_df.at[i, 'object_datatype'] = SQL_RDF_DATATYPE[data_type]
                        except:
                            pass
    return mappings_df


def parse_mappings(config):
    configuration, data_sources = _get_configuration_and_sources(config)

    mappings_df = pd.DataFrame(columns=MAPPINGS_DATAFRAME_COLUMNS)

    for source_name, source_options in data_sources.items():
        source_mappings_df = _parse_mapping_files(source_options, source_name)
        mappings_df = pd.concat([mappings_df, source_mappings_df])
        logging.info('Mappings for data source ' + str(source_name) + ' successfully parsed.')

    mappings_df = _remove_duplicated_mapping_rules(mappings_df)
    mappings_df = _rdf_class_to_pom(mappings_df)
    mappings_df = _set_pom_graphs(mappings_df)
    mappings_df = _complete_termtypes(mappings_df)
    mappings_df = _generate_mapping_partitions(mappings_df, configuration['mapping_partitions'])
    mappings_df = _complete_source_types(mappings_df, config)
    mappings_df = _remove_delimiters_from_identifiers(mappings_df)

    mappings_df = _infer_datatypes(mappings_df, config)

    _validate_mapping_partitions(mappings_df, configuration['mapping_partitions'])

    mappings_df.to_csv('m.csv', index=False)
    raise

    return mappings_df
