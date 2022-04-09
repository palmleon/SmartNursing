clear all
close all
clc
%% Library
import matlab.net.*
import matlab.net.http.*
%% API
mainAPI = "YTN43QRA4IWIEBIN";
%% Get request
r = RequestMessage;
uri = URI('https://api.thingspeak.com/channels.json?api_key=YTN43QRA4IWIEBIN');
resp = send(r,uri);
%% Retrive data, check and organise
len = length(resp.Body.Data);
for i=1:len
    channel = resp.Body.Data(i);
    data = thingSpeakRead(channel.id,'Fields',[2,3,4,6],NumPoints=8000,OutputFormat='timetable',ReadKey=channel.api_keys(2).api_key);
    perfusion_index = data(:,1).perfusionIndex;
    temperature = data(:,4).temperature;
    saturation = data(:,2).saturation;
    pulseRate = data(:,3).pulseRate;
% Remove NAN elements
    k=1;
    for j=1:length(perfusion_index)
        if ~isnan(perfusion_index(j))
                n_perfusion_index(k) = perfusion_index(j);
                k = k+1;
        end
    end
    k=1;
    for j=1:length(temperature)
        if ~isnan(temperature(j))
            n_temperature(k) = temperature(j);
            k = k+1;
        end
    end
    k = 1;
    for j=1:length(saturation)
        if ~isnan(saturation(j))
            n_saturation(k) = saturation(j);
            k = k +1;
        end
    end
    k = 1;
    for j=1:length(pulseRate)
        if ~isnan(pulseRate(j))
            n_pulseRate(k) = pulseRate(j);
            k = k +1;
        end
    end
    % check parameters and average
    sum_temp = 0;
    k = 0;
    for j=1:length(n_temperature)
        if n_temperature(j) >= 35
            sum_temp = sum_temp + n_temperature(j);
            k = k + 1;
        end
    end
    avg_temp(i) = sum_temp/k;
    sum_perfusion = 0;
    sum_saturation = 0;
    sum_pulse = 0;
    k = 0;
    for j=1:length(n_perfusion_index)
       if n_perfusion_index(j) > 4
            sum_perfusion = sum_perfusion + n_perfusion_index(j);
            sum_saturation = sum_saturation + n_saturation(j);
            sum_pulse = sum_pulse + n_pulseRate(j);
            k = k + 1;
       end
    end
    avg_pulse(i) = sum_pulse/k;
    avg_saturation(i) = sum_saturation/k;
    avg_perfusion(i) = sum_perfusion/k;
    % Visualize Data
    bar(1,avg_perfusion(i))
    hold on
    grid on
    bar(2,avg_saturation(i))
    hold on 
    grid on
    bar(3,avg_pulse(i))
    hold on
    grid on
    bar(4,avg_temp(i))
    hold on
    grid on
    title("title")
end