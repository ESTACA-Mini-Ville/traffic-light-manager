import time
import logging
import fastdds
# Import generated classes
# fastddsgen generates files like TrafficLight.py (if that's the module name) or classes in the file.
# Usually it generates a module per IDL or classes in the output dir.
# Assuming fastddsgen -python -d src/ src/TrafficLight.idl generates TrafficLight.py containing the classes.
# We might need to check the generated structure, but standard behavior is:
import TrafficLight

class DDSPublisher:
    def __init__(self, topic_name: str = "TrafficLightStatus", domain_id: int = 0):
        self.topic_name = topic_name
        self.domain_id = domain_id
        self.participant = None
        self.publisher = None
        self.topic = None
        self.writer = None
        self.type_support = None
        
        self._init_dds()

    def _init_dds(self):
        factory = fastdds.DomainParticipantFactory.get_instance()
        participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos(participant_qos)
        self.participant = factory.create_participant(self.domain_id, participant_qos)

        if self.participant is None:
            raise RuntimeError("Failed to create DomainParticipant")

        # Register Type using generated class
        self.topic_data_type = TrafficLight.TrafficLightStatusPubSubType()
        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        # Create Publisher
        publisher_qos = fastdds.PublisherQos()
        self.participant.get_default_publisher_qos(publisher_qos)
        self.publisher = self.participant.create_publisher(publisher_qos)

        # Create Topic
        topic_qos = fastdds.TopicQos()
        self.participant.get_default_topic_qos(topic_qos)
        self.topic = self.participant.create_topic(self.topic_name, self.type_support.get_type_name(), topic_qos)

        # Create DataWriter
        writer_qos = fastdds.DataWriterQos()
        self.publisher.get_default_datawriter_qos(writer_qos)
        self.writer = self.publisher.create_datawriter(self.topic, writer_qos)

    def publish(self, current_state: int, schedule: list):
        """
        schedule: list of objects with .state, .start_time, .duration
        """
        if self.writer is None:
            return

        # Create instance of generated class
        data = TrafficLight.TrafficLightStatus()
        data.current_state(current_state)
        data.timestamp(time.time())
        
        # Populate schedule sequence
        # The generated sequence usually has a specific API, often list-like or needing explicit append
        # For FastDDS Python, sequences are often just lists or have a .append method.
        # Let's assume list compatibility or helper method.
        
        schedule_seq = []
        for item in schedule:
            sched_item = TrafficLight.ScheduleItem()
            sched_item.state(int(item.state))
            sched_item.start_time(item.start_time)
            sched_item.duration(item.duration)
            schedule_seq.append(sched_item)
            
        data.schedule(schedule_seq)

        self.writer.write(data)

    def close(self):
        if self.participant:
            self.participant.delete_contained_entities()
            fastdds.DomainParticipantFactory.get_instance().delete_participant(self.participant)
