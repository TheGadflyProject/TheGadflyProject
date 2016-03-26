def replaceNth(sent, old, new, n):
    """Replaces the old with new at the nth index in sent
    Cite:inspectorG4dget http://stackoverflow.com/a/27589436"""
    inds = [i for i in range(len(sent) - len(old)+1)
            if sent[i:i+len(old)] == old]
    if len(inds) < n:
        return  # or maybe raise an error
    # can't assign to string slices. So, let's listify
    sent_list = list(sent)
    # do n-1 because we start from the first occurrence of the string,
    # not the 0-th
    sent_list[inds[n-1]:inds[n-1]+len(old)] = new
    return ''.join(sent_list)


def is_left_child(sent, root, entity):
    if sent.index(entity.text_with_ws) <= sent.index(root.text_with_ws):
        return True
    else:
        return False

if __name__ == "__main__":
    print("I'm just a utility module. Import me to use my code.")
