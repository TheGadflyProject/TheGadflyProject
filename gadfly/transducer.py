from spacy.tokens.token import Token

class Transducer:
    def _traverse_lefts(root):
        x = []
        for L in root.lefts:
            x = x + Transducer._traverse_lefts(L)
        if root.pos_ == "PUNCT":
            x.append(" ")
        else:
            x.append(root)
        return x

    def _traverse(root):
        x = []
        for R in root.rights:
            if R.pos_ == "PUNCT":
                continue
            x += Transducer._traverse(R)

        if root.pos_ in ["NOUN", "VERB"]:
            x = Transducer._traverse_lefts(root) + x
        else:
            x.insert(0, root)
        return x

    def transduce(parsed):
        for token in parsed:
            if token.head == token:
                root_token = token
                break
        traverse_list = Transducer._traverse(root_token)
        return "".join(
            [x.text_with_ws if type(x) == Token else x for x in traverse_list]
        )
