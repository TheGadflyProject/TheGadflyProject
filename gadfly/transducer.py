class Transducer:
    def _traverse_lefts(root):
        x = []
        for L in root.lefts:
            x = x + Transducer._traverse_lefts(L)
        if root.pos_ in ["ADP", "PUNCT"]:
            x.append(" ")
        else:
            x.append(root)
        return x

    def _traverse(root):
        x = []
        for R in root.rights:
            x += Transducer._traverse(R)

        if root.pos_ in ["NOUN", "VERB"]:
            x = Transducer._traverse_lefts(root) + x
        else:
            # prepend instead of append
            x.insert(0, root)
        return x

    def get_root_token(parsed):
        for token in parsed:
            if token.head == token:
                root_token = token
                break
        return root_token

    def transduce(parsed):
        root_token = Transducer.get_root_token(parsed)
        return Transducer._traverse(root_token)
