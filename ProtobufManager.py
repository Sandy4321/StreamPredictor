import PatternOfPatternsStream
import Protobuf.pop_pb2
import progressbar
from google.protobuf import text_format


class ProtobufManager:
    @staticmethod
    def tsv_to_protbuf(tsv_file):
        print 'Converting from tsv to protobuf the file ', tsv_file
        pm = PatternOfPatternsStream.PopManager()
        pm.load_tsv(tsv_file)
        buffy = ProtobufManager.PopManager_to_ProtobufPopManager(pm)
        ProtobufManager.save_protobuf(buffy, tsv_file[:-4] + '.pb')
        ProtobufManager.save_protobuf_plain(buffy, tsv_file[:-4] + '.pb.txt')

    @staticmethod
    def save_protobuf_plain(buffy, txt_file):
        f = open(txt_file, "w")
        f.write(text_format.MessageToString(buffy))
        f.close()

    @staticmethod
    def save_protobuf(buffy, pbfile):
        f = open(pbfile, "wb")
        f.write(buffy.SerializeToString())
        f.close()

    @staticmethod
    def PopManager_to_ProtobufPopManager(pm):
        print 'Converting from PopManager to ProtobufPopManager'
        buffy = Protobuf.pop_pb2.PopManager()
        bar, i = setup_progressbar(len(pm.patterns_collection))
        for pop in pm.patterns_collection.values():
            buffy_pop = buffy.pattern_collection.add()
            ProtobufManager.pop_to_protopop(buffy_pop, pop)
            bar.update(i + 1)
            i += 1
        bar.finish()
        return buffy

    @staticmethod
    def pop_to_protopop(buffy_pop, pop):
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

    @staticmethod
    def protobuf_to_tsv(pbfile):
        print 'Converting from protobuf to tsv the file ', pbfile
        pm = ProtobufManager.load_PopManager(pbfile)
        pm.save_tsv(pbfile + '.tsv')

    @staticmethod
    def load_PopManager(pbfile):
        buffy = ProtobufManager.load_buf(pbfile)
        pm = ProtobufManager.protobuf_to_popmanager(buffy)
        return pm

    @staticmethod
    def protobuf_to_popmanager(buffy):
        bar, i = setup_progressbar(len(buffy.pattern_collection))
        pm = PatternOfPatternsStream.PopManager()
        for bp in buffy.pattern_collection:
            pop = PatternOfPatternsStream.Pop(bp.unrolled_pattern)
            pop.strength = bp.strength
            pm.add_pop(pop)
            bar.update(i + 1)
            i += 1
        bar.finish()
        return pm

    @staticmethod
    def load_buf(pbfile):
        buffy = Protobuf.pop_pb2.PopManager()
        f = open(pbfile, "rb")
        buffy.ParseFromString(f.read())
        f.close()
        return buffy


def setup_progressbar(length):
    i = 0
    bar = progressbar.ProgressBar(maxval=length,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    return bar, i


if __name__ == '__main__':
    print 'File manager'
    ProtobufManager.tsv_to_protbuf('PatternStore/test.tsv')
    ProtobufManager.protobuf_to_tsv('PatternStore/test.pb')
