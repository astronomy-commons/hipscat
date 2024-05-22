from mocpy import MOC


def copy_moc(moc: MOC) -> MOC:
    return MOC.from_depth29_ranges(max_depth=moc.max_order, ranges=moc.to_depth29_ranges)
