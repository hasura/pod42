SET check_function_bodies = false;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
CREATE FUNCTION public.add_monotonic_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
nextval bigint;
BEGIN
  PERFORM pg_advisory_xact_lock(1);
  select nextval('serial_answers') into nextval;
  NEW.id := nextval;
  RETURN NEW;
END;
$$;
CREATE FUNCTION public.set_current_timestamp_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  _new record;
BEGIN
  _new := NEW;
  _new."updated_at" = NOW();
  RETURN _new;
END;
$$;
CREATE TABLE public.answers_slack (
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    answer text NOT NULL,
    sources text NOT NULL,
    id bigint NOT NULL,
    question_id bigint NOT NULL
);
CREATE SEQUENCE public.answers_slack_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.answers_slack_id_seq OWNED BY public.answers_slack.id;
CREATE TABLE public.questions_slack (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    question text NOT NULL,
    asked_by text NOT NULL
);
CREATE SEQUENCE public.questions_slack_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
CREATE SEQUENCE public.serial_answers
  START WITH 1
  INCREMENT BY 1
  NO MINVALUE
  NO MAXVALUE
  CACHE 1;
ALTER SEQUENCE public.questions_slack_id_seq OWNED BY public.questions_slack.id;
CREATE VIEW public.questions_with_answers AS
 SELECT a.id AS answer_id,
    a.question_id,
    q.question,
    a.answer,
    a.sources,
    q.asked_by
   FROM (public.questions_slack q
     JOIN public.answers_slack a ON ((a.question_id = q.id)));
ALTER TABLE ONLY public.answers_slack ALTER COLUMN id SET DEFAULT nextval('public.answers_slack_id_seq'::regclass);
ALTER TABLE ONLY public.questions_slack ALTER COLUMN id SET DEFAULT nextval('public.questions_slack_id_seq'::regclass);
ALTER TABLE ONLY public.answers_slack
    ADD CONSTRAINT answers_slack_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.questions_slack
    ADD CONSTRAINT questions_slack_pkey PRIMARY KEY (id);
CREATE UNIQUE INDEX answers_slack_question_id ON public.answers_slack USING btree (question_id);
CREATE TRIGGER add_monotonic_id_trigger BEFORE INSERT ON public.answers_slack FOR EACH ROW EXECUTE FUNCTION public.add_monotonic_id();
CREATE TRIGGER set_public_answers_slack_updated_at BEFORE UPDATE ON public.answers_slack FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_answers_slack_updated_at ON public.answers_slack IS 'trigger to set value of column "updated_at" to current timestamp on row update';
CREATE TRIGGER set_public_questions_slack_updated_at BEFORE UPDATE ON public.questions_slack FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_questions_slack_updated_at ON public.questions_slack IS 'trigger to set value of column "updated_at" to current timestamp on row update';
ALTER TABLE ONLY public.answers_slack
    ADD CONSTRAINT answers_slack_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions_slack(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
