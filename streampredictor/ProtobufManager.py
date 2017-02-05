import progressbar
from google.protobuf import text_format

import pop_pb2
import PopManager
import Pop
import StreamPredictor


class ProtobufManager:
    @staticmethod
    def tsv_to_protbuf(tsv_file):
        print 'Converting from tsv to protobuf the file ', tsv_file
        sp= StreamPredictor.StreamPredictor()
        sp.file_manager.load_tsv(tsv_file)
        buffy = ProtobufManager.PopManager_to_ProtobufPopManager(sp.pop_manager)
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
    def PopManager_to_ProtobufPopManager(pop_manager):
        print 'Converting from PopManager to ProtobufPopManager'
        buffy = pop_pb2.PopManager()
        bar, i = setup_progressbar(len(pop_manager.patterns_collection))
        for pop in pop_manager.patterns_collection.values():
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
        buffy_pop.category_members.extend([i.unrolled_pattern for i in pop.members_of_category])

    @staticmethod
    def protobuf_to_tsv(pbfile):
        print 'Converting from protobuf to tsv the file ', pbfile
        pm = ProtobufManager.load_PopManager(pbfile)
        sp = StreamPredictor.StreamPredictor(pm)
        sp.file_manager.save_tsv(pbfile + '.tsv')

    @staticmethod
    def load_PopManager(pbfile):
        buffy = ProtobufManager.load_buf(pbfile)
        pop_manager = ProtobufManager.protobuf_to_pop_manager(buffy)
        print 'Loaded pop manager with ', len(pop_manager.patterns_collection), ' patterns.'
        return pop_manager

    @staticmethod
    def protobuf_to_pop_manager(buffy):
        bar, i = setup_progressbar(2*len(buffy.pattern_collection))
        pop_manager = PopManager.PopManager()
        for bp in buffy.pattern_collection:
            pop = Pop.Pop(bp.unrolled_pattern)
            pop.strength = bp.strength
            pop_manager.add_pop(pop)
            bar.update(i + 1)
            i += 1
        for bp in buffy.pattern_collection:
            pop = pop_manager.patterns_collection[bp.unrolled_pattern]
            if bp.first_component:
                if bp.first_component in pop_manager.patterns_collection:
                    pop.first_component = pop_manager.patterns_collection[bp.first_component]
            if bp.second_component:
                if bp.second_component in pop_manager.patterns_collection:
                    pop.second_component = pop_manager.patterns_collection[bp.second_component]
            for parent_i in bp.first_child_parents:
                if parent_i in pop_manager.patterns_collection:
                    members = pop_manager.patterns_collection[parent_i]
                    pop.first_child_parents.append(members)
            if bp.belongs_to:
                pop.belongs_to_category = pop_manager.patterns_collection[bp.belongs_to]
            for cat in bp.category_members:
                member = pop_manager.patterns_collection[cat]
                pop.members_of_category.append(member)
            bar.update(i + 1)
            i += 1
        bar.finish()
        return pop_manager

    @staticmethod
    def load_buf(pbfile):
        buffy = pop_pb2.PopManager()
        f = open(pbfile, "rb")
        buffy.ParseFromString(f.read())
        f.close()
        return buffy

    @staticmethod
    def load_protobuf_plain(filename):
        buffy = pop_pb2.PopManager()
        f = open(filename, "r")
        text_format.Parse(f.read(), buffy)
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
    ProtobufManager.tsv_to_protbuf('../PatternStore/test.tsv')
    ProtobufManager.protobuf_to_tsv('../PatternStore/test.pb')
