import { inputSelector, useQRScoutState } from "@/store/store";
import { ImageInputData } from './BaseInputProps';
import { ConfigurableInputProps } from "./ConfigurableInput";


export default function(props: ConfigurableInputProps) {
    const data = useQRScoutState(
        inputSelector<ImageInputData>(props.section, props.code),
    );
} 