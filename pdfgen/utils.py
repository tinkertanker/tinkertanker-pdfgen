# -*- coding: utf-8 -*-


def split_text(text, max_length, calculate_length=len, inverse=False):
    words = text.split()
    word_count = len(words)
    if word_count > 1:
        splitter_range = range(1, word_count)
        if not inverse:
            splitter_range = list(reversed(splitter_range))
        candidate = (text, '')
        for i in splitter_range:
            left = ' '.join(words[:i])
            right = ' '.join(words[i:])
            long_side = right if inverse else left
            short_side = left if inverse else right
            long_side_length = calculate_length(long_side)
            short_side_length = calculate_length(short_side)
            if long_side_length < short_side_length:
                return candidate
            else:
                candidate = (left, right)
                if long_side_length < max_length:
                    return candidate
    else:
        return (text, '')


def equal_split_text(text, calculate_length=len):
    def generate_splitter(components):
        def splitter(index):
            left = ' '.join(components[:index])
            right = ' '.join(components[index:])
            left_length = calculate_length(left)
            right_length = calculate_length(right)
            length_diff = abs(left_length - right_length)
            return (length_diff, left, right)
        return splitter

    words = text.split()
    word_splitter = generate_splitter(words)
    word_count = len(words)
    if word_count > 1:
        possible_splits = [word_splitter(i) for i in range(1, word_count)]
        __, best_left, best_right = min(possible_splits)
        return best_left, best_right
    else:
        return text, ''
