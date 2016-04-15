from .q_generator_base import QGenerator


class HeuristicEvaluator:

    def check_titles(answer_span, question, answer_choices):
        if answer_span.label_ == "PERSON":
            # print("PERSON", q.answer)
            titles = ["Mr.", "Ms.", "Mrs."]
            words = question.split()
            index = words.index(QGenerator._GAP.strip())-1
            if index >= 0 and words[index] in titles:
                # print("BOOYAH")
                answer_choices = [name.split()[-1] for name
                                  in answer_choices]
        return list(set(answer_choices))

    def remove_apos_s_ans(ent, parsed_sentence):
        if "'s" in ent.text_with_ws:
            # we need to change the end pos
            # we need to change the entity
            return ent.end-1, \
                   parsed_sentence[ent.start:ent.end-1].text_with_ws.strip()
        return ent.end, ent.text_with_ws.strip()

    def remove_apos_s_choices(other_choices):
        for choice in other_choices:
            if "'s" in choice:
                choice = choice.replace("'s", "")
        return other_choices
