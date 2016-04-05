import PatternOfPatternsStream
import Protobuf.pop_pb2
import progressbar
from google.protobuf import text_format



def tsv_to_protbuf(tsv_file):
    print 'Converting from tsv to protobuf the file ', tsv_file
    pm = PatternOfPatternsStream.PopManager()
    pm.load_tsv(tsv_file)
    buffy = Protobuf.pop_pb2.PopManager()
    bar, i = setup_progressbar(len(pm.patterns_collection))
    for pop in pm.patterns_collection.values():
        buffy_pop = buffy.pattern_collection.add()
        buffy_pop.unrolled_pattern = pop.unrolled_pattern
        buffy_pop.strength = pop.strength
        if pop.first_component:
            buffy_pop.first_component = pop.first_component.unrolled_pattern
        if pop.second_component:
            buffy_pop.second_component = pop.second_component.unrolled_pattern
        buffy_pop.first_child_parents.extend([i.unrolled_pattern for i in pop.first_child_parents])
        if pop.belongs_to_category:
            buffy_pop.belongs_to = pop.belongs_to_category.unrolled_pattern
        buffy_pop.member_of.extend([i.unrolled_pattern for i in pop.members_of_category])
        bar.update(i + 1)
        i += 1
    bar.finish()
    f = open(tsv_file[:-4] + '.pb', "wb")
    f.write(buffy.SerializeToString())
    f.close()
    f = open(tsv_file[:-4] + '.pb.txt', "w")
    f.write(text_format.MessageToString(buffy))
    f.close()


def setup_progressbar(length):
    i = 0
    bar = progressbar.ProgressBar(maxval=length,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    return bar, i


def protobuf_to_tsv(pbfile):
    print 'Converting from protobuf to tsv the file ', pbfile
    buffy = Protobuf.pop_pb2.PopManager()
    f = open(pbfile, "rb")
    buffy.ParseFromString(f.read())
    f.close()
    pm = PatternOfPatternsStream.PopManager()
    bar, i = setup_progressbar(len(pm.patterns_collection))
    for bp in buffy.pattern_collection:
        pop = PatternOfPatternsStream.Pop(bp.unrolled_pattern)
        pop.strength = bp.strength
        pm.add_pop(pop)
        bar.update(i + 1)
        i += 1
    bar.finish()
    pm.save_tsv(pbfile + '.tsv')


if __name__ == '__main__':
    print 'File manager'
    tsv_to_protbuf('PatternStore/General.tsv')
    protobuf_to_tsv('PatternStore/General.pb')
