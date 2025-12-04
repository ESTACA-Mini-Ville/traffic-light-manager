import time
import logging
import fastdds
import TrafficLight

class DDSSubscriber:
    def __init__(self, topic_name: str = "TrafficLightStatus", domain_id: int = 0):
        self.topic_name = topic_name
        self.domain_id = domain_id
        self.participant = None
        self.subscriber = None
        self.topic = None
        self.reader = None
        self.type_support = None
        
        self._init_dds()

    def _init_dds(self):
        factory = fastdds.DomainParticipantFactory.get_instance()
        participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos(participant_qos)
        self.participant = factory.create_participant(self.domain_id, participant_qos)

        if self.participant is None:
            raise RuntimeError("Failed to create DomainParticipant")

        # Register Type
        self.topic_data_type = TrafficLight.TrafficLightStatusPubSubType()
        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        # Create Subscriber
        subscriber_qos = fastdds.SubscriberQos()
        self.participant.get_default_subscriber_qos(subscriber_qos)
        self.subscriber = self.participant.create_subscriber(subscriber_qos)

        # Create Topic
        topic_qos = fastdds.TopicQos()
        self.participant.get_default_topic_qos(topic_qos)
        self.topic = self.participant.create_topic(self.topic_name, self.type_support.get_type_name(), topic_qos)

        # Create DataReader
        reader_qos = fastdds.DataReaderQos()
        self.subscriber.get_default_datareader_qos(reader_qos)
        self.reader = self.subscriber.create_datareader(self.topic, reader_qos)

    def run(self):
        print("Waiting for data...")
        try:
            while True:
                if self.reader is not None:
                    info = fastdds.SampleInfo()
                    data = TrafficLight.TrafficLightStatus()
                    if self.reader.take_next_sample(data, info) == fastdds.RETCODE_OK:
                        if info.valid_data:
                            print(f"Received State: {data.current_state()}")
                            print(f"Timestamp: {data.timestamp()}")
                            print("Schedule:")
                            for item in data.schedule():
                                print(f"  - State: {item.state()}, Start: {item.start_time():.2f}, Duration: {item.duration()}")
                            print("-" * 20)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Stopping subscriber...")
        finally:
            if self.participant:
                self.participant.delete_contained_entities()
                fastdds.DomainParticipantFactory.get_instance().delete_participant(self.participant)

if __name__ == "__main__":
    subscriber = DDSSubscriber()
    subscriber.run()
