gri_standard_prompt = {
    'instruct_prompt': 'You are an expert in corporate disclosure with vast knowledge of climate change, human rights, ethics and social science, and expert in Global Reporting Initiative.'
                       'You are given paragraph and reporting standard descriptions. Your task is to predict standards that best align with the paragraph. Paragraph could be aligned utmost to 3 standards.'
                       'For the output, do not explain your decision and return relevant standard codes as Python with best matching standard as first element.',
    'examples': [
        {
            'input': '',
            'output': ''
        }
    ],
    'template': 'Paragraph: {paragraph}\n Standards: {standards}'
}

gri_disclosure_prompt = {
    'instruct_prompt': 'As an expert in climate policy and ESG framework reporting.'
                       'Paragraph was identified to be addressing following GRI standards: {standards}.'
                       'Identify which disclosures is the paragraph addressing specifically within the standards. A paragraph can address up to two disclosures.'
                       'For the output, do not explain your decision and return relevant disclosure codes as Python with best matching disclosure as first element.',
    'examples': [
        {
            'input': '',
            'output': ''
        }
    ],
    'template': 'Paragraph: {paragraph}\n Disclosures: {disclosures}'
}

scoring_agent_prompt = {
    'instruct_prompt': 'As a rating analyst, please assess the following paragraphs in terms of how well they address the specified GRI disclosures.'
                       'The paragraphs cover the following topic: {gri_standard}.'
                       '\nUse the scoring system below for Completeness and Materiality, assigning a score from the defined ranges.'
                       '\nCompletness Score on a scale of 0-10 wehere:\n9-10: Fully addresses the disclosure. Provides explicit and detailed information.\n5-8: Addresses the disclosure reasonably well. Covers most key elements but may lack specific examples or detail.\n1-4: Partially addresses the disclosure. Includes vague statements, omits key components, lacks clarity or depth.\n0: Does not address the disclosure at all.'
                       '\nMateriality Score on a scale of 0-10 wehere:\n9-10: Clearly demonstrates why the topic is important to the business and stakeholders. Shows alignment with strategy, risk, or stakeholder concerns.\n5-8: Indicates some relevance but lacks full context or explanation of significance. Generally aligns with stakeholder interest or business impact.\n1-4: Topic is mentioned without demonstrating why it matters. Minimal or no connection to business or stakeholders.\n0: No material connection; generic or boilerplate information irrelevant to the company context.'
                       'As an output create a list of JSON dictionaties for each disclosure code with completeness and matriality scores, and a comment,'
                       'following this format: "gri_disclosure": (GRI disclosure code),"completness": (0-10),"materiality": (0-10),"comment": (justify scores in one sentence)',
    'examples': [
        {
            'input': '',
            'output': ''
        }
    ],
    'template': 'Disclosures: {disclosures} \nParagraphs: {paragraphs}'
}

scoring_agent_disclosure_prompt = {
    'instruct_prompt': 'As a sustainability disclosure analyst, assess how well the following paragraphs address the specified GRI disclosure.'
                       '\nUse the scoring system below for Completeness and Materiality, assigning a score from the defined ranges.'
                       '\nCompletness, how fully disclosure is addressed, on a scale of 0-10 wehere:\n9-10: Fully addresses the disclosure. Provides explicit and detailed information.\n5-8: Addresses the disclosure reasonably well. Covers most key elements but may lack specific examples or detail.\n1-4: Partially addresses the disclosure. Includes vague statements, omits key components, lacks clarity or depth.\n0: Does not address the disclosure at all.'
                       '\nMateriality, how clear the improtance of disclosure is to company and stakeholders, on a scale of 0-10 wehere:\n9-10: Clearly demonstrates why the topic is important to the business and stakeholders. Shows alignment with strategy, risk, or stakeholder concerns.\n5-8: Indicates some relevance but lacks full context or explanation of significance. Generally aligns with stakeholder interest or business impact.\n1-4: Topic is mentioned without demonstrating why it matters. Minimal or no connection to business or stakeholders.\n0: No material connection; generic or boilerplate information irrelevant to the company context.'
                       'As an output create a JSON dictionary with completeness and matriality scores, and a comment,'
                       'strictly following this format: "completeness": (0-10),\n"materiality": (0-10),\n"comment": (justify each score briefly)',
    'examples': [
        {
            'input': '',
            'output': ''
        }
    ],
    'template': 'Disclosure: {disclosure} \nParagraphs: {paragraphs}'
}


def message_format(template, is_few_shot, params):
    messages = [{'role': 'system',
                 'content': template['instruct_prompt']}]
    if is_few_shot:
        for e in template['examples']:
            messages.append({
                'role': 'user',
                'content': e['input']
            })
            messages.append({
                'role': 'assistant',
                'content': e['output']
            })
    messages.append({
        'role': 'user',
        'content': template['template'].format(**params)
    })
    return messages